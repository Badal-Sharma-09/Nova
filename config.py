import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ADMIN_SECRET_CODE = os.getenv("ADMIN_SECRET_CODE")
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev_secret_key"
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
    WTF_CSRF_ENABLED = True
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/nova")
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    RATELIMIT_HEADERS_ENABLED = True
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    RATELIMIT_STORAGE_URI = "redis://localhost:6379"

    # Default Avatars List
    DEFAULT_AVATARS = [
        "https://api.dicebear.com/7.x/identicon/svg?seed=avatar1",
        "https://api.dicebear.com/7.x/identicon/svg?seed=avatar2",
        "https://api.dicebear.com/7.x/identicon/svg?seed=avatar3",
        "https://api.dicebear.com/7.x/identicon/svg?seed=avatar4",
        "https://api.dicebear.com/7.x/identicon/svg?seed=avatar5",
    ]
