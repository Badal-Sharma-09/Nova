from flask import Blueprint, render_template, session, jsonify, request, render_template, flash, redirect, url_for
from datetime import datetime
from flask_limiter.errors import RateLimitExceeded
from flask_wtf.csrf import CSRFError
from error_handlers import error_bp
from bson.objectid import ObjectId
from models.db import users_collection
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
import secrets
from PIL import Image
import io
from helpers.profile_utils import (
    is_valid_username, is_strong_password, passwords_match,
    allowed_image, is_valid_image_type, is_within_file_size_limit,
    save_profile_image, delete_old_image_if_needed
)

main_bp = Blueprint("main", __name__)

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE_MB = 2

@main_bp.route('/')
def index():
    username = session.get('username')
    return render_template('index.html', username=username)

@main_bp.route('/dashboard')
def dashboard():
    if not session.get('username'):
        flash('Please login to access the dashboard.', 'error')
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html', username=session.get('username'))

@main_bp.context_processor
def inject_now():
    return {'current_year': datetime.now().year}

@main_bp.route('/regenerate', methods=['POST'])
def regenerate():
    message_id = request.json['message_id']
    # Fetch context and re-run AI generation
    return jsonify({'new_response': "Here's a regenerated answer..."})

@main_bp.route("/profile")
def profile_view():
    if "username" not in session:
        flash("Please log in to view your profile.", "error")
        return redirect(url_for("auth.login"))

    user = users_collection.find_one({"_id": ObjectId(session["user_id"])})
    return render_template("profile.html", user=user)

def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(filename):
    ext = os.path.splitext(filename)[1]
    return f"{uuid.uuid4().hex}{ext}"

def file_size_within_limit(file):
    file.seek(0, os.SEEK_END)
    size_mb = file.tell() / (1024 * 1024)
    file.seek(0)
    return size_mb <= MAX_FILE_SIZE_MB

@main_bp.route("/profile/edit", methods=["GET", "POST"])
def edit_profile():
    if "user_id" not in session:
        flash("Please log in to edit your profile.", "error")
        return redirect(url_for("auth.login"))

    user = users_collection.find_one({"_id": ObjectId(session["user_id"])})
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        image = request.files.get("profile_image")

        # Validate username
        if not is_valid_username(username):
            flash("Username must be alphanumeric (3–20 chars) and not a number.", "error")
            return redirect(request.url)

        if users_collection.find_one({"username": username, "_id": {"$ne": user["_id"]}}):
            flash("Username already taken.", "error")
            return redirect(request.url)

        # Gmail users can't change email
        if user.get("password") is None and email != user.get("email"):
            flash("Google-authenticated users can't change email.", "error")
            return redirect(request.url)

        # Password validation (if provided)
        if password:
            if not is_strong_password(password):
                flash("Password must be 8+ characters and include uppercase, lowercase, digit, and special char.", "error")
                return redirect(request.url)
            if not passwords_match(password, confirm_password):
                flash("Passwords do not match.", "error")
                return redirect(request.url)
            hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
        else:
            hashed_pw = user.get("password")

        # Image validation and saving
        profile_image_url = user.get("profile_image")
        if image and image.filename != "":
            if not allowed_image(image.filename) or not is_valid_image_type(image):
                flash("Only image files (png, jpg, jpeg, gif) are allowed.", "error")
                return redirect(request.url)
            if not is_within_file_size_limit(image):
                flash("Image size exceeds 2MB.", "error")
                return redirect(request.url)

            # Save and update
            delete_old_image_if_needed(profile_image_url)
            profile_image_url = save_profile_image(image)

        # Update user
        users_collection.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "username": username,
                    "email": email,
                    "password": hashed_pw,
                    "profile_image": profile_image_url
                }
            },
        )

        session["username"] = username
        session["email"] = email
        session["profile_image"] = profile_image_url

        flash("Profile updated successfully!", "success")
        return redirect(url_for("main.profile_view"))

    return render_template("edit_profile.html", user=user)
