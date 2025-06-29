from flask import Blueprint, render_template, session, redirect, url_for, flash
from models.db import users_collection, db, contacts_collection, chat_history_collection, otp_collection
from functools import wraps
from bson.objectid import ObjectId

admin_bp = Blueprint("admin", __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash("You do not have permission to access this page.", "error")
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    # Only allow access if the user is logged in and is an admin
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized access", "danger")
        return redirect(url_for('auth.login'))

    # Retrieve dynamic statistics from MongoDB
    total_users = users_collection.count_documents({})
    contact_submissions = contacts_collection.count_documents({})
    # If you have a messages collection, you might do:
    # new_messages = messages_collection.count_documents({'status': 'new'})
    # For now, we'll set new_messages to a dummy value (adjust as needed)
    new_messages = 0

    return render_template('admin_dashboard.html',
                           username=session.get('username'),
                           total_users=total_users,
                           new_messages=new_messages,
                           contact_submissions=contact_submissions)

@admin_bp.route('/admin/contacts')
def admin_contacts():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized access", "danger")
        return redirect(url_for('login'))

    contacts = list(contacts_collection.find().sort("timestamp", -1))
    return render_template('admin_contacts.html', contacts=contacts)

@admin_bp.route('/admin/manage_users')
@admin_required
def manage_users():
    # For now, simply query all users (or a subset) and pass it to a template.
    users = list(users_collection.find().sort("username", 1))
    return render_template('manage_users.html', users=users)

@admin_bp.route("/admin/contacts")
def view_contacts():
    if not session.get("is_admin"):
        flash("Unauthorized access", "error")
        return redirect(url_for("main.index"))

    all_contacts = contacts_collection.find().sort("_id", -1)  # Show latest first
    return render_template("admin_contacts.html", contacts=all_contacts)

@admin_bp.route("/admin/contacts/delete/<contact_id>", methods=["POST"])
def delete_contact(contact_id):
    if not session.get("is_admin"):
        flash("Unauthorized access", "error")
        return redirect(url_for("main.index"))

    contacts_collection.delete_one({"_id": ObjectId(contact_id)})
    flash("Contact deleted successfully.", "success")
    return redirect(url_for("admin.view_contacts"))

@admin_bp.route("/admin/toggle_block/<user_id>", methods=["POST"])
def toggle_block_user(user_id):
    if not session.get("is_admin"):
        flash("Unauthorized access", "error")
        return redirect(url_for("main.index"))

    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        new_status = not user.get("is_blocked", False)
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_blocked": new_status}}
        )
        flash(f"User {'unblocked' if not new_status else 'blocked'} successfully.", "success")
    else:
        flash("User not found.", "error")

    return redirect(url_for("admin.manage_users"))
