import os
import secrets
import logging
from datetime import timedelta
from dotenv import load_dotenv


load_dotenv()

logger = logging.getLogger("config")


class Config:
    """Base configuration with security and database settings."""

    # Secret key with validation
    SECRET_KEY = (
        os.getenv("SECRET_KEY")
        or os.getenv("FLASK_SECRET")
        or secrets.token_urlsafe(32)
    )

    # Warn if using generated secret key
    if not os.getenv("SECRET_KEY") and not os.getenv("FLASK_SECRET"):
        logger.warning(
            "SECRET_KEY not set in environment. Using generated key. "
            "This will cause sessions to be invalidated on restart!"
        )

    # Session configuration
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(
        hours=int(os.getenv("SESSION_TIMEOUT_HOURS", 12))
    )
    WTF_CSRF_TIME_LIMIT = int(os.getenv("CSRF_TIME_LIMIT", 3600))

    # File upload configuration
    MAX_CONTENT_LENGTH = int(
        os.getenv("MAX_CONTENT_LENGTH", 10 * 1024 * 1024)
    )  # 10MB default
    ALLOWED_EXTENSIONS = set(os.getenv("ALLOWED_EXTENSIONS", "txt").split(","))

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///whatsanalyzer.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    }

    # Redis/Celery configuration for background tasks
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "app.log")
    LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 10 * 1024 * 1024))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 5))

    @staticmethod
    def enforce_security(app):
        """Apply runtime security tweaks that depend on deployment flags."""
        secure_cookies = os.getenv("ENABLE_HTTPS", "false").lower() in {
            "1",
            "true",
            "yes",
        }
        # Only enable secure (HTTPS-only) cookies when HTTPS is explicitly
        # requested and the app is running in production. In development
        # environments setting secure cookies breaks local testing and can
        # cause missing CSRF session tokens.
        is_production = (
            os.getenv("FLASK_ENV", "").lower() == "production"
            or str(app.config.get("ENV", "")).lower() == "production"
        )
        if secure_cookies and is_production:
            app.config.setdefault("SESSION_COOKIE_SECURE", True)
            app.config.setdefault("REMEMBER_COOKIE_SECURE", True)
            logger.info("Secure cookies enabled for production HTTPS")
        else:
            # Ensure cookies are usable in development/testing by default.
            app.config.setdefault("SESSION_COOKIE_SECURE", False)
            app.config.setdefault("REMEMBER_COOKIE_SECURE", False)
            if is_production:
                logger.warning(
                    "Running in production without HTTPS. "
                    "Set ENABLE_HTTPS=true for secure cookies."
                )

        # Set file upload limits from environment
        app.config.setdefault(
            "MAX_CONTENT_LENGTH", int(os.getenv("MAX_CONTENT_LENGTH", 10 * 1024 * 1024))
        )

    @staticmethod
    def validate_required_settings():
        """Validate that required settings are present."""
        required = []
        warnings = []

        # Check for production requirements
        if os.getenv("FLASK_ENV", "").lower() == "production":
            if not os.getenv("SECRET_KEY") and not os.getenv("FLASK_SECRET"):
                required.append("SECRET_KEY or FLASK_SECRET must be set in production")

            if not os.getenv("ENABLE_HTTPS", "false").lower() in {"1", "true", "yes"}:
                warnings.append(
                    "ENABLE_HTTPS not set in production - consider enabling HTTPS"
                )

        # Log warnings
        for warning in warnings:
            logger.warning(warning)

        # Raise error for missing required settings
        if required:
            raise ValueError("Missing required configuration:\n" + "\n".join(required))


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
