"""
Django settings for config project.

Environment (production VM + Supabase):
  SECRET_KEY                — required in production (long random string)
  DJANGO_DEBUG             — False in production ("0", "false", "no")
  DJANGO_ALLOWED_HOSTS     — comma-separated, e.g. example.com,www.example.com,1.2.3.4
  DATABASE_URL             — Supabase Postgres URI (include sslmode=require)
  DJANGO_CSRF_TRUSTED_ORIGINS — optional; comma-separated https:// origins when using HTTPS
  DJANGO_USE_X_FORWARDED_PROTO — set "1" when behind nginx/apache with X-Forwarded-Proto
"""

import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-dev-only-change-in-production-w$zx%1p#-_9x#0b",
)

DJANGO_DEBUG = os.environ.get("DJANGO_DEBUG", "True").strip().lower()
DEBUG = DJANGO_DEBUG in ("1", "true", "yes")

_allowed = os.environ.get("DJANGO_ALLOWED_HOSTS", "").strip()
if _allowed:
    ALLOWED_HOSTS = [h.strip() for h in _allowed.split(",") if h.strip()]
elif DEBUG:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]
else:
    ALLOWED_HOSTS = []

_csrf_origins = os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").strip()
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in _csrf_origins.split(",") if o.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "holisticmap",
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

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
_ssl_require = os.environ.get("DATABASE_SSL_REQUIRE", "True").strip().lower() in ("1", "true", "yes")
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=_ssl_require,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

if not DEBUG:
    WHITENOISE_MANIFEST_STRICT = False
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }

if not DEBUG:
    _use_fwd = (
        os.environ.get("DJANGO_USE_X_FORWARDED_PROTO", "").strip().lower()
        in ("1", "true", "yes")
    )
    if _use_fwd:
        SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

_DEFAULT = object()

def _bool_env(key: str, default: bool) -> bool:
    raw = os.environ.get(key, _DEFAULT)
    if raw is _DEFAULT:
        return default
    return str(raw).strip().lower() in ("1", "true", "yes")

if not DEBUG and _bool_env("DJANGO_SECURE_SSL_REDIRECT", True):
    SECURE_SSL_REDIRECT = True
