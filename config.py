import os
import secrets
from datetime import timedelta
from dotenv import load_dotenv


load_dotenv()


class Config:
    SECRET_KEY = (
        os.getenv("SECRET_KEY")
        or os.getenv("FLASK_SECRET")
        or secrets.token_urlsafe(32)
    )
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
    WTF_CSRF_TIME_LIMIT = 3600

    @staticmethod
    def enforce_security(app):
        """Apply runtime security tweaks that depend on deployment flags."""
        secure_cookies = os.getenv("ENABLE_HTTPS", "false").lower() in {
            "1",
            "true",
            "yes",
        }
        app.config.setdefault("SESSION_COOKIE_SECURE", secure_cookies)
        app.config.setdefault("REMEMBER_COOKIE_SECURE", secure_cookies)
        app.config.setdefault(
            "MAX_CONTENT_LENGTH", int(os.getenv("MAX_CONTENT_LENGTH", 5 * 1024 * 1024))
        )


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
