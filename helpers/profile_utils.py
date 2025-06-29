import os, re, uuid
from werkzeug.utils import secure_filename
from flask import current_app, url_for
from PIL import Image

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
MAX_FILE_SIZE_MB = 2

def is_valid_username(username):
    return bool(re.match(r"^[a-zA-Z0-9_]{3,20}$", username)) and not username.isnumeric()

def is_strong_password(password):
    return bool(re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&]).{8,}$", password))

def passwords_match(password, confirm_password):
    return password == confirm_password

def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_image_type(file_storage):
    try:
        img = Image.open(file_storage.stream)
        return img.format.lower() in ALLOWED_EXTENSIONS
    except Exception:
        return False

def is_within_file_size_limit(file_storage):
    file_storage.seek(0, os.SEEK_END)
    size_mb = file_storage.tell() / (1024 * 1024)
    file_storage.seek(0)
    return size_mb <= MAX_FILE_SIZE_MB

def generate_unique_filename(filename):
    ext = os.path.splitext(filename)[1]
    return f"{uuid.uuid4().hex}{ext}"

def save_profile_image(image):
    filename = generate_unique_filename(secure_filename(image.filename))
    path = os.path.join(current_app.root_path, "static/uploads", filename)
    image.save(path)
    return url_for("static", filename=f"uploads/{filename}")

def delete_old_image_if_needed(current_url):
    if current_url and "default-avatar.png" not in current_url:
        old_path = os.path.join(current_app.root_path, current_url.replace("/static/", "static/"))
        if os.path.exists(old_path):
            os.remove(old_path)
