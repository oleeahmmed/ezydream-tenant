import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"
ALLOWED_HOSTS = [h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]

SHARED_APPS = [
    "django_tenants",
    "apps.core",
    "django.contrib.contenttypes",
    "unfold",
    "unfold.contrib.filters",
    "django.contrib.admin",
    "django.contrib.auth",
    "apps.auth",
    "apps.warehouse",
    "apps.inventory",
    "apps.sales",
    "apps.purchase",
    "apps.production",
    "apps.finance",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_bolt",
]

# django-tenants: TENANT_APPS cannot be empty. ERP apps live in each tenant schema.
TENANT_APPS = [
    "django.contrib.contenttypes",
    "apps.auth",
    "apps.warehouse",
    "apps.inventory",
    "apps.sales",
    "apps.purchase",
    "apps.production",
    "apps.finance",
]

# Password-reset token validity (hours)
AUTH_PASSWORD_RESET_HOURS = int(os.getenv("AUTH_PASSWORD_RESET_HOURS", "24"))
# Bolt JWT lifetime for tenant User login (seconds)
AUTH_ACCESS_TOKEN_SECONDS = int(os.getenv("AUTH_ACCESS_TOKEN_SECONDS", str(60 * 60)))
AUTH_REFRESH_TOKEN_SECONDS = int(
    os.getenv("AUTH_REFRESH_TOKEN_SECONDS", str(60 * 60 * 24 * 7))
)
AUTH_OTP_LENGTH = int(os.getenv("AUTH_OTP_LENGTH", "6"))
AUTH_OTP_VALID_SECONDS = int(os.getenv("AUTH_OTP_VALID_SECONDS", "600"))

AUTH_USER_MODEL = "tenant_auth.User"

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@localhost")
SERVER_EMAIL = DEFAULT_FROM_EMAIL

INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]

TENANT_MODEL = "core.Client"
TENANT_DOMAIN_MODEL = "core.Domain"

MIDDLEWARE = [
    "django_tenants.middleware.main.TenantMainMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
PUBLIC_SCHEMA_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": os.getenv(
            "DB_ENGINE",
            "django_tenants.postgresql_backend",
        ),
        "NAME": os.getenv("DB_NAME", "ezydream_erp"),
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

from ..unfold_settings import UNFOLD  # noqa: E402
