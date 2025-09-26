import os
from pathlib import Path
import dj_database_url
from .settings import *

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-your-secret-key-here')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.onrender.com'] + (
    [RENDER_EXTERNAL_HOSTNAME] if RENDER_EXTERNAL_HOSTNAME else []
)

# CSRF: доверяем доменам Render
CSRF_TRUSTED_ORIGINS = ['https://*.onrender.com'] + (
    [f"https://{RENDER_EXTERNAL_HOSTNAME}"] if RENDER_EXTERNAL_HOSTNAME else []
)

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# База данных: используем PostgreSQL, если DATABASE_URL задан;
# иначе оставляем конфиг из базовых настроек (SQLite)
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Simplified static file serving.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security settings for Render
SECURE_SSL_REDIRECT = True
# Учитываем заголовок прокси от Render, чтобы избежать редирект-лупа
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SAMESITE = 'Strict'

# Enable CSP middleware for production (совместимо с django-csp 3.x)
MIDDLEWARE = [
    'csp.middleware.CSPMiddleware',
] + MIDDLEWARE

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_CONNECT_SRC = ("'self'", "https:")
CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",
    "https://fonts.googleapis.com",
    "https://cdn.jsdelivr.net",
    "https://cdnjs.cloudflare.com",
)
CSP_FONT_SRC = (
    "'self'",
    "https://fonts.gstatic.com",
    "https://cdnjs.cloudflare.com",
)
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-inline'",
    "'unsafe-eval'",
    "https://cdn.jsdelivr.net",
    "https://www.google.com",
    "https://www.gstatic.com",
)
CSP_FRAME_SRC = (
    "'self'",
    "https://www.google.com",
)

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Silence system check for reCAPTCHA test keys in production until real keys are set
SILENCED_SYSTEM_CHECKS = list(globals().get('SILENCED_SYSTEM_CHECKS', [])) + [
    'django_recaptcha.recaptcha_test_key_error'
]
