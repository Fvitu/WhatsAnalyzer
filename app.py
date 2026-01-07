from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from flask_wtf.csrf import CSRFProtect
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    current_user,
)
from config import config, Config
import os
import logging
from db_manager import DatabaseManager
from werkzeug.utils import secure_filename
from whatsapp_statistics import (
    parse_chat,
    analyze_messages,
)
import json

# Modelos
from models.ModelUser import ModelUser

# Entidades
from models.entities.User import User

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
)
logger = logging.getLogger("app")

env = os.getenv("FLASK_ENV", "development")
config_class = config.get(env, Config)

app = Flask(__name__)
app.config.from_object(config_class)
config_class.enforce_security(app)
csrf = CSRFProtect(app)


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
        ],
        "CSP_EXTRA_STYLE_SRC",
    )
    font_sources = _merge_csp_sources(
        [
            "'self'",
            "https://cdn.jsdelivr.net",
            "https://site-assets.fontawesome.com",
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


# Inicializar el gestor de base de datos
db_manager = DatabaseManager.get_instance()

login_manager_app = LoginManager(app)

# Configuración para subida de archivos
UPLOAD_FOLDER = os.path.join(app.instance_path, "uploads")
ALLOWED_EXTENSIONS = {"txt"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config.setdefault(
    "MAX_CONTENT_LENGTH", int(os.getenv("MAX_CONTENT_LENGTH", 5 * 1024 * 1024))
)

SECURITY_HEADERS = {
    "Content-Security-Policy": _build_content_security_policy(),
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
}

# Crear carpeta uploads si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@login_manager_app.user_loader
def load_user(id):
    try:
        return ModelUser.get_by_id(db_manager, id)
    except Exception as e:
        return None


# Manejador de errores para conexiones de base de datos
def handle_db_error(e):
    logger.error(f"Error de base de datos: {e}")
    flash(
        "Ha ocurrido un error de conexión a la base de datos. Inténtelo de nuevo en unos momentos."
    )
    return redirect(url_for("dashboard"))


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


@app.route("/register", methods=["GET", "POST"])
def register():
    try:
        if current_user.is_authenticated:
            # Si el usuario ya está autenticado, redirige al home
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]
            confirm_password = request.form["confirm_password"]

            if password == confirm_password:
                if not ModelUser.is_email_taken(db_manager, email):
                    new_user = User(
                        0, username=username, password=password, email=email
                    )
                    logged_user = ModelUser.register(db_manager, new_user)
                    if logged_user is not None and logged_user.password:
                        # Loguea automáticamente al usuario recién registrado
                        login_user(logged_user)
                        flash(
                            "Usuario creado como '{}', ahora inicia sesión".format(
                                username
                            )
                        )
                        return redirect(url_for("login"))
                else:
                    flash("Este email ya está en uso...")
            else:
                flash("Las contraseñas no coinciden...")

        # Renderiza el template auth/register.html
        return render_template("auth/register.html")
    except Exception as e:
        logger.error(f"Error en registro: {e}")
        flash(
            "Ha ocurrido un error durante el registro. Por favor, inténtelo de nuevo."
        )
        return redirect(url_for("register"))


@app.route("/login", methods=["GET", "POST"])
def login():
    try:
        if current_user.is_authenticated:
            # Si el usuario ya está autenticado, redirige al home
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            remember = "remember" in request.form
            user = User(0, request.form["username"], request.form["password"])
            logged_user = ModelUser.login(db_manager, user)

            if logged_user is not None and logged_user.password:
                login_user(logged_user, remember)
                return redirect(url_for("dashboard"))
            else:
                flash("Usuario o contraseña incorrectos...")

        return render_template("auth/login.html")
    except Exception as e:
        logger.error(f"Error en login: {e}")
        flash(
            "Ha ocurrido un error durante el inicio de sesión. Por favor, inténtelo de nuevo."
        )
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    try:
        # Datos por defecto (vacíos o de ejemplo) para cuando entra por GET
        analysis_data = None

        if request.method == "POST":
            # Verificar si el post tiene la parte del archivo
            if "chatFile" not in request.files:
                flash("No se encontró el archivo")
                return redirect(request.url)

            file = request.files["chatFile"]

            if file.filename == "":
                flash("No se seleccionó ningún archivo")
                return redirect(request.url)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)

                try:
                    # 1. Analizar el archivo usando tu lógica existente
                    # Nota: Modifiqué un poco el flujo para no depender de process_chat escribiendo json en disco
                    messages = parse_chat(filepath)
                    stats = analyze_messages(messages)

                    # 2. Pasamos los datos a la variable que irá al template
                    analysis_data = stats

                    flash("¡Análisis completado con éxito!")

                except Exception as e:
                    logger.error(f"Error analizando el chat: {e}")
                    flash(f"Error al procesar el archivo: {str(e)}")
                finally:
                    # 3. Limpieza: Borrar el archivo subido por privacidad
                    if os.path.exists(filepath):
                        os.remove(filepath)
            else:
                flash("Formato de archivo no permitido. Solo se admite .txt")

        # Si hay datos de análisis, los pasamos. Si no, pasamos None.
        # Serializamos a JSON string para que JS lo pueda leer fácilmente
        stats_json = (
            json.dumps(analysis_data, ensure_ascii=False) if analysis_data else "null"
        )

        return render_template(
            "dashboard.html", stats_json=stats_json  # Variable clave para el frontend
        )

    except Exception as e:
        logger.error(f"Error en dashboard: {e}")
        flash(f"Ha ocurrido un error inesperado.")
        return render_template("error.html")


@app.route("/protected")
def protected():
    return "<h1>No tienes acceso a esta sección, por favor inicia sesión.</h1>"


def status_401(error):
    return redirect(url_for("dashboard"))


def status_404(error):
    return "<h1>Página no encontrada.</h1>"


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
