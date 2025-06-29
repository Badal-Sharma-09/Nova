from flask import Blueprint, render_template, redirect, url_for, flash
from forms.contact_form import ContactForm
from datetime import datetime
from models.db import contacts_collection
from extensions import limiter
from flask import request
import re

contact_bp = Blueprint("contact", __name__)

@contact_bp.route("/contact", methods=["GET", "POST"])
# @limiter.limit("3 per minute; 10 per hour", methods=["POST"])
def contact():
    if request.method == "POST":
        name = f"{request.form.get('first_name')} {request.form.get('last_name')}"
        email = request.form.get("email")
        message = request.form.get("message")
        company = request.form.get("company")
        phone = request.form.get("phone")

        if not all([name.strip(), email.strip(), message.strip()]):  # Basic check
            flash("Please fill out all required fields.", "error")
            return redirect(url_for("contact.contact"))

        # Add to MongoDB
        contact_entry = {
            "name": name,
            "email": email,
            "message": message,
            "company": company,
            "phone": phone,
            "timestamp": datetime.utcnow()
        }
        contacts_collection.insert_one(contact_entry)

        flash("Thank you! Your message has been sent.", "success")
        return redirect(url_for("contact.contact"))

    return render_template("contact.html")
