# utils/otp.py
from flask_mail import Message
from extensions import mail
from datetime import datetime, timedelta
from extensions import limiter
from flask import Blueprint, request, render_template, flash, redirect, url_for
from datetime import datetime, timedelta
from flask_mail import Message
from extensions import mail
from models.db import users_collection
from models.otp import otp_collection
import os
import random

otp_bp = Blueprint("otp", __name__)

def generate_otp():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def send_otp_email(to_email, otp_code):
    msg = Message(
        subject="Your OTP Code",
        sender=os.getenv("MAIL_USERNAME"),
        recipients=[to_email],
        body=f"Your verification code is: {otp_code}"
    )
    mail.send(msg)
    
@otp_bp.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    email = request.args.get('email') if request.method == 'GET' else request.form.get('email')

    if not email:
        flash("Missing email or OTP. Please try again.", "error")
        return redirect(url_for('auth.register'))

    if request.method == 'POST':
        entered_otp = request.form.get('otp')

        if not entered_otp:
            flash("Please enter the OTP.", "error")
            return render_template('otp.html', email=email)

        otp_entry = otp_collection.find_one({'email': email})
        if not otp_entry:
            flash("OTP not found or expired. Please register again.", "error")
            return redirect(url_for('auth.register'))

        if datetime.utcnow() > otp_entry.get('expires_at', datetime.utcnow()):
            flash("OTP has expired. Please request a new one.", "error")
            return redirect(url_for('auth.register'))

        if otp_entry['otp'] != entered_otp:
            flash("Incorrect OTP. Please try again.", "error")
            return render_template('otp.html', email=email)

        users_collection.update_one({'email': email}, {'$set': {'is_verified': True}})
        otp_collection.delete_one({'email': email})

        user = users_collection.find_one({'email': email})
        print(f"User {user.get('username')} verified with role: {user.get('role')}")

        flash("OTP verified successfully! You can now login.", "success")
        return redirect(url_for('auth.login'))

    return render_template('otp.html', email=email)

# Split route so limiter applies only to POST requests
@otp_bp.route("/send_otp", methods=["GET"])
def show_send_otp_form():
    return render_template("register.html")

@otp_bp.route('/send_otp', methods=['POST'])
@limiter.limit("3 per minute; 10 per hour", methods=["POST"])
def send_otp():
    email = request.form.get('email')
    otp = str(random.randint(100000, 999999))

    otp_collection.update_one(
        {"email": email},
        {"$set": {
            "otp": otp,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=5),
            "last_sent": datetime.utcnow(),
            "resend_count": 1,
            "attempt_count": 0
        }},
        upsert=True
    )

    msg = Message('Your OTP Code', sender=os.getenv("MAIL_USERNAME"), recipients=[email])
    msg.body = f"Your OTP code is: {otp}"
    mail.send(msg)

    return render_template('otp.html', email=email)

# Split route so limiter applies only to POST requests
@otp_bp.route("/resend_otp", methods=["GET"])
def show_register_form():
    return render_template("register.html")

@otp_bp.route('/resend_otp', methods=['POST'])
@limiter.limit("3 per minute; 10 per hour", methods=["POST"])
def resend_otp():
    email = request.form.get('email')
    record = otp_collection.find_one({"email": email})

    if not record:
        flash("OTP request not found. Please register again.", "danger")
        return redirect(url_for('auth.register'))

    now = datetime.utcnow()
    last_sent = record.get('last_sent', now - timedelta(minutes=10))
    resend_count = record.get('resend_count', 0)

    if resend_count >= 3 and (now - last_sent).total_seconds() < 600:
        flash("You've exceeded the resend limit. Try again later.", "danger")
        return render_template('otp.html', email=email)

    otp = str(random.randint(100000, 999999))

    otp_collection.update_one(
        {"email": email},
        {
            "$set": {
                "otp": otp,
                "expires_at": now + timedelta(minutes=5),
                "last_sent": now
            },
            "$inc": {"resend_count": 1}
        }
    )

    msg = Message('Your Resent OTP Code', sender=os.getenv("MAIL_USERNAME"), recipients=[email])
    msg.body = f"Your new OTP code is: {otp}"
    mail.send(msg)

    flash("A new OTP has been sent to your email.", "success")
    return render_template('otp.html', email=email)

# Utility for account setup (usually from register)
def set_otp_for_user(email):
    otp = generate_otp()
    now = datetime.utcnow()

    users_collection.update_one(
        {"email": email},
        {
            "$set": {
                "otp": otp,
                "otp_generated_at": now,
                "otp_attempts": 0,
                "otp_resend_count": 1,
                "otp_first_resend_time": now
            }
        },
        upsert=True
    )
    send_otp_email(email, otp)
