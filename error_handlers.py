from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_wtf.csrf import CSRFError

error_bp = Blueprint('errors', __name__)

@error_bp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@error_bp.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@error_bp.errorhandler(429)
def ratelimit_error(e):
    # Password reset rate limit UI
    if request.method == 'POST' and request.endpoint == 'forgot_bp.forgot_password':
        flash("Too many password reset attempts. Please try again later.", "warning")
        return redirect(url_for('forgot.forgot_password'))

    # AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"error": "Rate limit exceeded"}), 429

    # Default error page
    return render_template('429.html', error="You're doing that too much. Please wait and try again."), 429

@error_bp.app_errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template("csrf_expired.html"), 400

@error_bp.route('/feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    message_id = data.get('message_id')
    feedback_type = data.get('type')
    # Store feedback in DB, log, etc.
    return jsonify({"status": "ok"})
