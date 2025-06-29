from utils.mailer import send_reset_email
from flask import render_template, request, redirect, flash, url_for
import extensions
from extensions import bcrypt, limiter, s
from models.db import users_collection
from flask import Blueprint
from itsdangerous import SignatureExpired, BadSignature

forgot_bp = Blueprint("forgot", __name__)

# Split route so limiter applies only to POST requests
@forgot_bp.route("/reset-password/<token>", methods=["GET"])
def show_reset_password_form(token):
    return render_template("reset_password.html", token=token)

@forgot_bp.route('/reset-password/<token>', methods=["POST"])
@limiter.limit("3 per minute; 10 per hour", methods=["POST"])
def reset_password(token):
    try:
        email = extensions.s.loads(token, salt='password-reset-salt', max_age=3600)
    except SignatureExpired:
        flash('🔒 Your reset link has expired. Please request a new one.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    except BadSignature:
        flash('Invalid or tampered link.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('reset_password.html')

        hashed_pw = bcrypt.generate_password_hash(new_password).decode('utf-8')
        result = users_collection.update_one({'email': email}, {'$set': {'password': hashed_pw}})
        if result.modified_count == 0:
            flash('Password update failed. Please try again.', 'danger')
        else:
            flash('Your password has been updated!', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password.html')

@forgot_bp.route("/forgot-password", methods=["GET"])
def show_forgot_password_form():
    return render_template("forgot_password.html")

@forgot_bp.route('/forgot-password', methods=["POST"])
# @limiter.limit("2 per minute; 5 per hour", methods=["POST"])
def forgot_password():
    email = request.form.get('email')
    user = users_collection.find_one({'email': email})

    if user:
        if extensions.s is None:
            raise RuntimeError("Serializer is not initialized. Check if init_serializer() was called.")

        # Only run if serializer is available
        token = extensions.s.dumps(email, salt='password-reset-salt')
        send_reset_email(email, token)
        flash('A password reset link has been sent to your email.', 'info')
    else:
        flash('No account found with that email.', 'danger')

    return redirect(url_for('auth.login'))
