"""
Production settings for danovmusic_studio project on Vercel.
"""

from .settings import *
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Vercel specific settings
ALLOWED_HOSTS = [
    '.vercel.app',
    '.now.sh',
    'localhost',
    '127.0.0.1',
]

# Add your custom domain here if you have one
# ALLOWED_HOSTS.append('yourdomain.com')

# Static files settings for Vercel
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# WhiteNoise configuration for static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security settings for production (simplified for Vercel)
SECURE_SSL_REDIRECT = False  # Vercel handles SSL
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = False  # Vercel handles this
CSRF_COOKIE_SECURE = False  # Vercel handles this
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'  # More permissive for Vercel
CSRF_COOKIE_SAMESITE = 'Lax'  # More permissive for Vercel

# Enable CSP middleware for production
MIDDLEWARE.insert(1, 'csp.middleware.CSPMiddleware')

# Content Security Policy for production
CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': {
        'connect-src': ("'self'", 'https:'),
        'default-src': ("'self'",),    
        'font-src': ("'self'",
                     'https://fonts.gstatic.com',
                     'https://cdnjs.cloudflare.com'),
        'frame-src': ("'self'", 'https://www.google.com'),
        'img-src': ("'self'", 'data:', 'https:'),
        'media-src': ("'self'",),      
        'script-src': ("'self'",       
                       "'unsafe-inline'",
                       'https://www.google.com',
                       'https://www.gstatic.com',
                       'https://cdn.jsdelivr.net'),
        'style-src': ("'self'",        
                      "'unsafe-inline'",
                      'https://fonts.googleapis.com',
                      'https://cdn.jsdelivr.net',
                      'https://cdnjs.cloudflare.com')
    }
}

# Database settings for Vercel (using SQLite for simplicity)
# For production, consider using PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 30,
        }
    }
}

# Logging configuration
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
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
} 