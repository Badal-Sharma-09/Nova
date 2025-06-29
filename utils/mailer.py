from flask_mail import Message
from flask import url_for, current_app
from extensions import mail

def send_reset_email(to_email, token):
    reset_url = url_for('forgot.reset_password', token=token, _external=True)
    msg = Message(
        subject='Password Reset Request',
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[to_email],
        body=f'''To reset your password, click the following link:
{reset_url}

If you did not request this, please ignore this email.
'''
    )
    mail.send(msg)
