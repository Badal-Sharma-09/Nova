from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Regexp, Email, Optional

class ContactForm(FlaskForm):
    first_name = StringField('First Name', validators=[
        DataRequired(), 
        Regexp(r'^[A-Za-z\s]+$', message="Only letters and spaces allowed.")
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(), 
        Regexp(r'^[A-Za-z\s]+$', message="Only letters and spaces allowed.")
    ])
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(message="Invalid email address.")
    ])
    company = StringField('Company', validators=[DataRequired()])
    phone = StringField('Phone', validators=[
        Optional(), 
        Regexp(r'^\d*$', message="Phone must contain only digits.")
    ])
    message = TextAreaField('Message', validators=[DataRequired()])
