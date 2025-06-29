from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from werkzeug.security import check_password_hash
from forms.auth_forms import LoginForm
from models.db import users_collection, db
from extensions import s, oauth, bcrypt, mail
from models.otp import otp_collection
from datetime import datetime, timedelta
from flask_mail import Message
from utils.token import generate_token, confirm_token
from utils.otp import generate_otp, send_otp_email
from extensions import limiter
from flask import current_app
import random
import os
import re

FAILED_ATTEMPT_LIMIT = 5
LOCKOUT_DURATION = timedelta(minutes=15)

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("3 per minute; 10 per hour", methods=["POST"])
def login():
    form = LoginForm()

    if request.method == "POST" and form.validate_on_submit():
        user_input = form.username.data
        password = form.password.data

        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        username_pattern = r"^[A-Za-z0-9_]+$"
        password_pattern = (
            r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
        )

        if not user_input or not password:
            flash("All fields are required.", "error")
            return render_template("login.html", form=form)

        user = None
        if re.match(email_pattern, user_input):
            user = users_collection.find_one({"email": user_input})
            lookup_key = user_input
        elif re.match(username_pattern, user_input):
            user = users_collection.find_one({"username": user_input})
            lookup_key = user_input
        else:
            flash("Invalid username or email format.", "error")
            return render_template("login.html", form=form)

        if not re.match(password_pattern, password):
            flash("Invalid password format.", "error")
            return render_template("login.html", form=form)

        if not user:
            flash("No account found. Please register first.", "error")
            return render_template("login.html", form=form)

        if user.get("is_blocked"):
            flash("Your account has been blocked. Contact admin.", "error")
            return render_template("login.html", form=form)

        # Rate limiting logic
        now = datetime.utcnow()
        login_attempt = db.login_attempts.find_one({"user_key": lookup_key})

        if login_attempt:
            failed_attempts = login_attempt.get("count", 0)
            last_attempt_time = login_attempt.get("last_failed", now)

            if failed_attempts >= FAILED_ATTEMPT_LIMIT:
                if now - last_attempt_time < LOCKOUT_DURATION:
                    remaining = LOCKOUT_DURATION - (now - last_attempt_time)
                    mins, secs = divmod(int(remaining.total_seconds()), 60)
                    flash(
                        f"Too many failed attempts. Try again in {mins}m {secs}s.",
                        "error",
                    )
                    return render_template("login.html", form=form)
                else:
                    db.login_attempts.update_one(
                        {"user_key": lookup_key},
                        {"$set": {"count": 0, "last_failed": now}},
                    )

        hashed_pw = user.get("password")
        if not hashed_pw:
            flash(
                "This account was registered using Google. Please log in with Google.",
                "error",
            )
            return render_template("login.html", form=form)

        try:
            if bcrypt.check_password_hash(hashed_pw, password):
                db.login_attempts.delete_one({"user_key": lookup_key})

                session["user_id"] = str(user["_id"])
                session["username"] = user.get("username")
                session["role"] = user.get("role", "user")
                session["is_admin"] = user.get("role") == "admin"

                flash("Login successful!", "success")
                return redirect(
                    url_for(
                        "admin.admin_dashboard" if session["is_admin"] else "main.index"
                    )
                )
            else:
                if login_attempt:
                    db.login_attempts.update_one(
                        {"user_key": lookup_key},
                        {"$inc": {"count": 1}, "$set": {"last_failed": now}},
                    )
                else:
                    db.login_attempts.insert_one(
                        {"user_key": lookup_key, "count": 1, "last_failed": now}
                    )
                flash("Incorrect password. Please try again.", "error")

        except ValueError:
            flash("Invalid password format.", "error")

    return render_template("login.html", form=form)

@auth_bp.route("/login/google", methods=["GET", "POST"])
@limiter.limit("3 per minute; 10 per hour", methods=["POST"])
def google_login():
    try:
        google = oauth.create_client("google")
        redirect_uri = url_for("auth.google_authorize", _external=True)
        return google.authorize_redirect(redirect_uri=redirect_uri, prompt="select_account")
    except Exception as e:
        flash("Google login failed. Check server logs.", "error")
        return redirect(url_for("auth.login"))

@auth_bp.route("/login/google/authorize")
def google_authorize():
    google = oauth.create_client("google")
    token = google.authorize_access_token()
    user_info = google.get("userinfo").json()

    if not user_info:
        flash("Failed to authenticate with Google.", "error")
        return redirect(url_for("auth.login"))

    email = user_info.get("email")
    name = user_info.get("name")
    # profile_image = user_info.get("picture") or random.choice(DEFAULT_AVATARS)
    profile_image = random.choice(current_app.config["DEFAULT_AVATARS"])

    user = users_collection.find_one({"email": email})

    # Check if user is blocked
    if user and user.get("is_blocked"):
        flash("Your account has been blocked. Contact admin.", "error")
        return redirect(url_for("auth.login"))

    if not user:
        user_data = {
            "username": name,
            "email": email,
            "password": None,
            "role": "user",
            "is_verified": True,
            "created_at": datetime.utcnow(),
            "profile_image": profile_image,
        }
        inserted_id = users_collection.insert_one(user_data).inserted_id
        session["user_id"] = str(inserted_id)
        session["role"] = "user"
        session["is_admin"] = False
        flash("Registration successful!", "success")
    else:
        session["user_id"] = str(user["_id"])
        session["role"] = user.get("role", "user")
        session["is_admin"] = user.get("role") == "admin"
        flash("Login successful!", "success")

        # Use stored image if available, fallback to Google image or random
        profile_image = user.get("profile_image") or profile_image

    session["username"] = name
    session["email"] = email
    session["profile_image"] = profile_image

    return redirect(
        url_for("admin.admin_dashboard" if session.get("is_admin") else "main.index")
    )


# Split route so limiter applies only to POST requests
@auth_bp.route("/register", methods=["GET"])
def show_register_form():
    return render_template("register.html")


@auth_bp.route("/register", methods=["POST"])
@limiter.limit("3 per minute; 10 per hour", methods=["POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password")
        secret_code = request.form.get("secret_code")
        print("secret code:", secret_code)
        print("email:", email)

        username_pattern = r"^[a-zA-Z0-9_]{3,20}$"
        email_pattern = r"^[\w\.-]+@gmail\.com$"
        password_pattern = (
            r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
        )

        if not all([username, email, password]):
            flash("All fields are required.", "error")
            return render_template("register.html")

        if not re.match(username_pattern, username):
            flash("Invalid username format.", "error")
            return render_template("register.html")

        if not re.match(email_pattern, email):
            flash("Invalid Gmail address.", "error")
            return render_template("register.html")

        if not re.match(password_pattern, password):
            flash("Weak password.", "error")
            return render_template("register.html")

        existing_username_user = users_collection.find_one({"username": username})
        if existing_username_user:
            if existing_username_user.get("is_verified"):
                flash("Username already exists.", "error")
                return render_template("register.html")
            elif existing_username_user.get("email") != email:
                flash(
                    "Username already taken and pending verification. Choose another.",
                    "error",
                )
                return render_template("register.html")
            else:
                created_at = existing_username_user.get("created_at")
                if created_at and datetime.utcnow() - created_at > timedelta(
                    minutes=10
                ):
                    users_collection.delete_one({"username": username})
                else:
                    new_otp = generate_otp()
                    otp_collection.update_one(
                        {"email": email},
                        {
                            "$set": {
                                "otp": new_otp,
                                "expires_at": datetime.utcnow() + timedelta(minutes=5),
                            }
                        },
                        upsert=True,
                    )
                    send_otp_email(email, new_otp)
                    flash("A new OTP has been sent to your email.", "info")
                    return redirect(url_for("otp.verify_otp", email=email))

        existing_email_user = users_collection.find_one({"email": email})
        if existing_email_user:
            if existing_email_user.get("is_verified"):
                flash("Email already registered and verified. Please login.", "error")
                return render_template("register.html")
            else:
                created_at = existing_email_user.get("created_at")
                if created_at and datetime.utcnow() - created_at > timedelta(
                    minutes=10
                ):
                    users_collection.delete_one({"email": email})
                else:
                    new_otp = generate_otp()
                    otp_collection.update_one(
                        {"email": email},
                        {
                            "$set": {
                                "otp": new_otp,
                                "expires_at": datetime.utcnow() + timedelta(minutes=5),
                            }
                        },
                        upsert=True,
                    )
                    send_otp_email(email, new_otp)
                    flash("A new OTP has been sent to your email.", "info")
                    return redirect(url_for("otp.verify_otp", email=email))

        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

        profile_image = random.choice(current_app.config["DEFAULT_AVATARS"])
        user_data = {
            "username": username,
            "email": email,
            "password": hashed_pw,
            "role": (
                "admin" if secret_code == os.getenv("ADMIN_SECRET_CODE") else "user"
            ),
            "is_verified": False,
            "created_at": datetime.utcnow(),
            "profile_image": profile_image,
        }

        users_collection.insert_one(user_data)

        otp_code = generate_otp()
        otp_collection.update_one(
            {"email": email},
            {
                "$set": {
                    "otp": otp_code,
                    "expires_at": datetime.utcnow() + timedelta(minutes=5),
                }
            },
            upsert=True,
        )
        send_otp_email(email, otp_code)

        flash("OTP sent to your email. Please verify.", "info")
        return redirect(url_for("otp.verify_otp", email=email))

    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("main.index"))


@auth_bp.route("/cleanup_unverified")
def cleanup_unverified():
    cutoff = datetime.utcnow() - timedelta(minutes=10)
    result = users_collection.delete_many(
        {"is_verified": False, "created_at": {"$lt": cutoff}}
    )
    return f"Deleted {result.deleted_count} stale unverified users."
