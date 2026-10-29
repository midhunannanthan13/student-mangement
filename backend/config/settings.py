"""
Django settings for the Student Management System (backend).

All secrets and server addresses come from environment variables:
  * on your laptop  -> they are read from backend/.env
  * on Vercel       -> you type them in Project > Settings > Environment Variables
"""
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Read the settings file (default: backend/.env). It silently does nothing when the
# file does not exist, e.g. on Vercel, where variables are typed in the dashboard.
# To use another file for ONE command, set ENV_FILE, e.g. ENV_FILE=.env.aiven
ENV_FILE_IN_USE = os.getenv("ENV_FILE", ".env")
load_dotenv(BASE_DIR / ENV_FILE_IN_USE)


def env_list(name):
    """Turn 'a, b ,c' into ['a', 'b', 'c'] (empty values are ignored)."""
    return [item.strip().rstrip("/") for item in os.getenv(name, "").split(",") if item.strip()]


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
DEBUG = os.getenv("DEBUG", "False").strip().lower() == "true"

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "dev-only-insecure-key-do-not-use-in-production"
    else:
        raise ImproperlyConfigured("SECRET_KEY is missing. Add it to backend/.env or to the Vercel environment variables.")

ALLOWED_HOSTS = ["127.0.0.1", "localhost", ".vercel.app"] + env_list("ALLOWED_HOSTS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "students",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # must stay at the top
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# ---------------------------------------------------------------------------
# CORS: which frontends may call this API
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5500",  # VS Code Live Server
    "http://localhost:5500",
] + env_list("CORS_ALLOWED_ORIGINS")  # e.g. https://your-frontend.vercel.app


# ---------------------------------------------------------------------------
# Database
#   DB_HOST filled in  -> MySQL: your local MySQL Workbench / WAMP server, or Aiven
#   DB_HOST left empty -> SQLite file, only for a very quick local test
#   DB_SSL_CA filled   -> encrypted connection (REQUIRED by Aiven)
# ---------------------------------------------------------------------------
DB_HOST = os.getenv("DB_HOST", "").strip()

if DB_HOST:
    db_options = {"charset": "utf8mb4", "connect_timeout": 15}

    ssl_ca = os.getenv("DB_SSL_CA", "").strip()
    if ssl_ca:
        ca_path = Path(ssl_ca)
        if not ca_path.is_absolute():
            ca_path = BASE_DIR / ca_path  # e.g. certs/aiven-ca.pem inside backend/
        if not ca_path.is_file():
            raise ImproperlyConfigured(
                f"DB_SSL_CA points to a file that does not exist: {ca_path}. "
                "Download the CA certificate from the Aiven console and save it there."
            )
        # Checks that the server certificate was issued by the Aiven CA ("verify-ca",
        # the mode Aiven's own documentation uses).
        db_options["ssl"] = {"ca": str(ca_path), "check_hostname": False}

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("DB_NAME"),
            "USER": os.getenv("DB_USER"),
            "PASSWORD": os.getenv("DB_PASSWORD"),
            "HOST": DB_HOST,
            "PORT": os.getenv("DB_PORT", "3306"),
            "OPTIONS": db_options,
        }
    }
elif os.getenv("VERCEL"):
    # Vercel cannot keep a SQLite file, so a missing database must be a loud error.
    raise ImproperlyConfigured("DB_HOST is missing. Add DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT and DB_SSL_CA in the Vercel environment variables.")
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    # Production answers with JSON only. The browsable API page is a local helper.
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"]
    + (["rest_framework.renderers.BrowsableAPIRenderer"] if DEBUG else []),
    # Learning project: the API is public (no login). See the guide for next steps.
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
}


# ---------------------------------------------------------------------------
# Passwords, language, static files
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
