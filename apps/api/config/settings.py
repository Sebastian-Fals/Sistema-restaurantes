import os
from pathlib import Path

# Carga opcional de apps/api/.env (no dependencia externa).
_env_file = Path(__file__).resolve().parent.parent / ".env"
if _env_file.is_file():
    for _line in _env_file.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#") or "=" not in _line:
            continue
        _key, _, _val = _line.partition("=")
        _key, _val = _key.strip(), _val.strip()
        if _key and _key not in os.environ:
            os.environ[_key] = _val

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name: str, default: bool) -> bool:
    return os.environ.get(name, str(default)).lower() in ("1", "true", "yes")


DEBUG = env_bool("DEBUG", False)
SECRET_KEY = os.environ.get("SECRET_KEY") or ("dev-only-insecure-key" if DEBUG else "")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY es obligatorio cuando DEBUG=false")

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
_raw_csrf = os.environ.get("CSRF_TRUSTED_ORIGINS", "")
if not _raw_csrf and DEBUG:
    _raw_csrf = "http://localhost:3000,http://127.0.0.1:3000"
CSRF_TRUSTED_ORIGINS = [o for o in _raw_csrf.split(",") if o]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "mesa.identity",
    "mesa.loyalty",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

# Producción: DATABASE_URL apunta al PostgreSQL externo. SQLite solo para desarrollo/tests.
# La base de datos es SIEMPRE externa (PostgreSQL). No hay SQLite local.
_database_url = os.environ.get("DATABASE_URL")
if not _database_url:
    raise RuntimeError(
        "DATABASE_URL es obligatorio (PostgreSQL externo). "
        "Configuralo en apps/api/.env o en el entorno. No se usa SQLite local."
    )
DATABASES = {"default": dj_database_url.config(default=_database_url)}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "identity.User"

LANGUAGE_CODE = "es-co"
TIME_ZONE = "America/Bogota"
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# El navegador habla con Next.js (mismo origen); Next reenvía /api al backend.
SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = env_bool("COOKIE_SECURE", not DEBUG)
CSRF_COOKIE_HTTPONLY = False  # el frontend lee la cookie para enviar X-CSRFToken
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.SessionAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],  # denegar por defecto
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "mesa.loyalty.api.errors.exception_handler",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Mesa API",
    "DESCRIPTION": "Programa de sellos para cafeterías (piloto).",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
}

# Correo: Resend si hay API key; si no, consola (desarrollo y tests).
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
RESEND_FROM = os.environ.get("RESEND_FROM", "Mesa <no-reply@example.com>")
MAIL_ADAPTER = os.environ.get("MAIL_ADAPTER", "resend" if RESEND_API_KEY else "console")
