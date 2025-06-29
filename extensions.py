from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer
from authlib.integrations.flask_client import OAuth
from redis import Redis
from flask_bcrypt import Bcrypt

# === Flask Extensions ===
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=[])
mail = Mail()
oauth = OAuth()
bcrypt = Bcrypt()

# === Globals Initialized Later ===
redis_connection = None
s = None  # Serializer instance
google = None  # Optional if we're assigning this globally, otherwise skip

# === Initializers ===
def init_redis(app):
    """Initialize Redis connection from Flask app config."""
    global redis_connection
    redis_connection = Redis(
        host=app.config.get("REDIS_HOST", "localhost"),
        port=app.config.get("REDIS_PORT", 6379),
        db=app.config.get("REDIS_DB", 0)
    )

def init_serializer(secret_key):
    global s
    s = URLSafeTimedSerializer(secret_key)
