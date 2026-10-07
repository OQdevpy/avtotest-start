"""AvtoStart — Django sozlamalari.

Barcha maxfiy qiymatlar muhit o'zgaruvchilaridan olinadi. DEBUG=False bo'lganda
SECRET_KEY, BIN_STORAGE_KEY va ALLOWED_HOSTS majburiy.
"""
import os
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def env(name, default=None):
    return os.environ.get(name, default)


def env_bool(name, default=False):
    return env(name, str(default)).lower() in ("1", "true", "yes", "on")


def env_list(name, default=""):
    return [x.strip() for x in env(name, default).split(",") if x.strip()]


DEBUG = env_bool("DEBUG", False)

SECRET_KEY = env("SECRET_KEY")
# DB'da saqlanadigan sessiya kalitlarini shifrlash uchun alohida kalit (32 bayt, base64).
BIN_STORAGE_KEY = env("BIN_STORAGE_KEY")
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS")

if DEBUG:
    SECRET_KEY = SECRET_KEY or "dev-insecure-secret-key-change-me"
    BIN_STORAGE_KEY = BIN_STORAGE_KEY or "ZGV2LWluc2VjdXJlLWJpbi1zdG9yYWdlLWtleS0zMmI="
    ALLOWED_HOSTS = ALLOWED_HOSTS or ["localhost", "127.0.0.1"]
else:
    missing = [n for n, v in (("SECRET_KEY", SECRET_KEY), ("BIN_STORAGE_KEY", BIN_STORAGE_KEY),
                              ("ALLOWED_HOSTS", ALLOWED_HOSTS)) if not v]
    if missing:
        raise ImproperlyConfigured(f"Majburiy o'zgaruvchilar yo'q: {', '.join(missing)}")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "apps.accounts",
    "apps.content",
    "apps.exams",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "binproto.middleware.SecurityHeadersMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "binproto.middleware.CorsMiddleware",
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

if env("DB_NAME"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("DB_NAME"),
            "USER": env("DB_USER", "postgres"),
            "PASSWORD": env("DB_PASSWORD", ""),
            "HOST": env("DB_HOST", "db"),
            "PORT": env("DB_PORT", "5432"),
            "CONN_MAX_AGE": 60,
        }
    }
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

CACHES = {
    "default": (
        {"BACKEND": "django.core.cache.backends.redis.RedisCache", "LOCATION": env("REDIS_URL")}
        if env("REDIS_URL")
        else {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "uz"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# Media fayllar ommaviy URL orqali BERILMAYDI — faqat shifrlangan /api/media/*.bin orqali.
MEDIA_ROOT = Path(env("MEDIA_ROOT", BASE_DIR / "media"))
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["binproto.auth.DeviceSessionAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": ["binproto.renderers.BinRenderer"],
    "DEFAULT_PARSER_CLASSES": ["binproto.parsers.BinParser"],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "30/min",
        "user": "600/min",
        "login": env("LOGIN_RATE", "5/min"),
    },
    "UNAUTHENTICATED_USER": None,
    "EXCEPTION_HANDLER": "binproto.exceptions.exception_handler",
}

# --- .bin protokoli ---
BIN_SESSION_TTL = timedelta(hours=int(env("BIN_SESSION_TTL_HOURS", "12")))
BIN_MAX_CLOCK_SKEW = int(env("BIN_MAX_CLOCK_SKEW", "120"))  # soniya
EXAM_DURATION = timedelta(minutes=int(env("EXAM_DURATION_MINUTES", "25")))
EXAM_DURATION_LONG = timedelta(minutes=int(env("EXAM_DURATION_LONG_MINUTES", "45")))
EXAM_LONG_THRESHOLD = int(env("EXAM_LONG_THRESHOLD", "20"))
LOGIN_MAX_FAILS = int(env("LOGIN_MAX_FAILS", "10"))  # bir IP uchun, 15 daqiqada
SHUFFLE_ANSWERS = env_bool("SHUFFLE_ANSWERS", False)

CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS", "http://localhost:5173" if DEBUG else "")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")

# --- HTTPS va xavfsizlik sarlavhalari ---
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
    SECURE_REDIRECT_EXEMPT = [r"^api/health/$"]
    SECURE_HSTS_SECONDS = int(env("SECURE_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

ADMIN_URL = env("ADMIN_URL", "boshqaruv-7f3a/")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "security": {"handlers": ["console"], "level": "INFO"},
        "django.security": {"handlers": ["console"], "level": "WARNING"},
    },
}
