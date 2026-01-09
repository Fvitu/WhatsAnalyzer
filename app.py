from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from flask_wtf.csrf import CSRFProtect
from config import config, Config
import os
import logging
import io
import time
from whatsapp_statistics import (
    analyze_messages,
    parse_chat_stream,
)
import json
from utils import FileValidator, format_file_size


# Configure minimal logging - NO file logging for privacy
def setup_logging(app):
    """Configure minimal console-only logging. NO files, NO user data stored."""
    log_level = logging.ERROR  # Only errors, not info about files/users

    # Simple formatter without sensitive details
    simple_formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler ONLY - no file logging for privacy
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(simple_formatter)
    console_handler.setLevel(log_level)

    # Configure app logger
    app.logger.handlers = []
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)


logger = logging.getLogger("app")

env = os.getenv("FLASK_ENV", "development")
config_class = config.get(env, Config)

app = Flask(__name__)
app.config.from_object(config_class)

# Setup minimal logging
setup_logging(app)

# Validate configuration
try:
    config_class.validate_required_settings()
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    raise

config_class.enforce_security(app)

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize file validator
file_validator = FileValidator(
    allowed_extensions=app.config.get("ALLOWED_EXTENSIONS", {"txt"}),
    max_size_bytes=app.config.get("MAX_CONTENT_LENGTH", 10 * 1024 * 1024),
)


def _merge_csp_sources(defaults, env_key):
    """Combine default CSP sources with optional space-delimited additions."""
    sources = list(defaults)
    extras = os.getenv(env_key, "").split()
    for source in extras:
        if source and source not in sources:
            sources.append(source)
    return sources


def _build_content_security_policy():
    script_sources = _merge_csp_sources(
        [
            "'self'",
            "'unsafe-inline'",
            "https://cdn.jsdelivr.net",
            "https://code.jquery.com",
        ],
        "CSP_EXTRA_SCRIPT_SRC",
    )
    style_sources = _merge_csp_sources(
        [
            "'self'",
            "'unsafe-inline'",
            "https://cdn.jsdelivr.net",
            "https://site-assets.fontawesome.com",
            "https://fonts.googleapis.com",
        ],
        "CSP_EXTRA_STYLE_SRC",
    )
    font_sources = _merge_csp_sources(
        [
            "'self'",
            "https://cdn.jsdelivr.net",
            "https://site-assets.fontawesome.com",
            "https://fonts.gstatic.com",
            "data:",
        ],
        "CSP_EXTRA_FONT_SRC",
    )
    img_sources = _merge_csp_sources(["'self'", "data:"], "CSP_EXTRA_IMG_SRC")
    connect_sources = _merge_csp_sources(
        ["'self'", "https://cdn.jsdelivr.net"], "CSP_EXTRA_CONNECT_SRC"
    )

    directives = {
        "default-src": ["'self'"],
        "script-src": script_sources,
        "style-src": style_sources,
        "font-src": font_sources,
        "img-src": img_sources,
        "connect-src": connect_sources,
        "form-action": ["'self'"],
        "base-uri": ["'self'"],
        "frame-ancestors": ["'none'"],
        "object-src": ["'none'"],
    }

    return "; ".join(
        f"{directive} {' '.join(sources)}" for directive, sources in directives.items()
    )


# Configuración para subida de archivos
UPLOAD_FOLDER = os.path.join(app.instance_path, "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Crear carpeta uploads si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

SECURITY_HEADERS = {
    "Content-Security-Policy": _build_content_security_policy(),
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "X-XSS-Protection": "1; mode=block",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
}


@app.after_request
def apply_security_headers(response):
    for header, value in SECURITY_HEADERS.items():
        response.headers.setdefault(header, value)
    if app.config.get("SESSION_COOKIE_SECURE"):
        response.headers.setdefault(
            "Strict-Transport-Security", "max-age=63072000; includeSubDomains"
        )
    return response


@app.route("/")
def index():
    return redirect(url_for("dashboard"))


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    """Main dashboard"""
    try:
        analysis_data = None

        if request.method == "POST":
            # Check if file is in request
            if "chatFile" not in request.files:
                flash("File not found in the request", "error")
                return redirect(request.url)

            file = request.files["chatFile"]

            # Validate file using FileValidator
            is_valid, error_message, metadata = file_validator.validate_file(file)

            if not is_valid:
                flash(error_message, "error")
                return redirect(request.url)

            file_size = metadata["size"]

            try:
                start_time = time.time()

                # Read file content (in memory only)
                raw_bytes = file.stream.read()
                if not raw_bytes:
                    flash("The file is empty", "error")
                    return redirect(request.url)

                # Decode with fallback encoding
                try:
                    text_content = raw_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    text_content = raw_bytes.decode("latin-1")

                # Parse and analyze chat (all in memory, no storage)
                messages = parse_chat_stream(io.StringIO(text_content))

                if not messages:
                    flash("No valid WhatsApp messages found in the file", "warning")
                    return redirect(request.url)

                # Analyze messages
                stats = analyze_messages(messages)
                analysis_data = stats

                processing_time = time.time() - start_time

                # Success message emphasizing privacy
                flash(
                    f"Analysis completed! Processed {len(messages)} messages in {processing_time:.2f}s. "
                )

            except ValueError as ve:
                flash(f"Invalid file format: {str(ve)}", "error")
            except UnicodeDecodeError:
                flash(
                    "Unable to read file. Please ensure it's a text file with UTF-8 or Latin-1 encoding",
                    "error",
                )
            except Exception as e:
                flash(f"Error processing the file: {str(e)}", "error")

        stats_json = (
            json.dumps(analysis_data, ensure_ascii=False) if analysis_data else "null"
        )

        return render_template("dashboard.html", stats_json=stats_json)

    except Exception as e:
        flash("An unexpected error occurred. Please try again.", "error")
        return render_template("error.html", error=str(e))


def status_401(error):
    return redirect(url_for("dashboard"))


def status_404(error):
    return "<h1>Page not found.</h1>"


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    max_mb = app.config.get("MAX_CONTENT_LENGTH", 0) / (1024 * 1024)
    flash(f"File too large. Maximum size allowed: {max_mb:.1f}MB", "error")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    env = os.getenv("FLASK_ENV", "development")
    config_class = config.get(env, Config)
    app.config.from_object(config_class)
    config_class.enforce_security(app)
    csrf.init_app(app)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
