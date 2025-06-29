from flask import Flask
from config import Config
from extensions import csrf, limiter, mail, init_serializer, init_redis, oauth, bcrypt, s
from routes.main import main_bp
from routes.auth import auth_bp
from routes.contact import contact_bp
from routes.chat import chat_bp
from routes.admin import admin_bp
from routes.forget_password import forgot_bp
from authlib.integrations.flask_client import OAuthError
from utils.otp import otp_bp
from extensions import limiter
from dotenv import load_dotenv
from error_handlers import error_bp

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(Config)

    # Extensions
    init_serializer(app.config["SECRET_KEY"])
    oauth.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    mail.init_app(app)
    init_redis(app)
    bcrypt.init_app(app)

    # OAuth provider setup
    oauth.register(
        name="google",
        client_id=app.config.get("GOOGLE_CLIENT_ID"),
        client_secret=app.config.get("GOOGLE_CLIENT_SECRET"),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        redirect_uri=app.config.get("GOOGLE_REDIRECT_URI"),
        client_kwargs={
            "scope": "openid profile email",
            "jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
        },
        api_base_url="https://openidconnect.googleapis.com/v1/",
    )

    # Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(otp_bp)
    app.register_blueprint(forgot_bp)
    app.register_blueprint(error_bp)

    return app
