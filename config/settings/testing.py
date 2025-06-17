"""
Testing settings para Tech Ecommerce.
"""

from .base import *

# Debug en testing
DEBUG = True

# Database para testing - en memoria
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

# Cache para testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Email backend para testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Media y static files para testing
MEDIA_ROOT = '/tmp/tech_ecommerce_test_media'
STATIC_ROOT = '/tmp/tech_ecommerce_test_static'

# Password hashers más rápidos para testing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Celery sincrono para testing
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Logging mínimo para testing
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
        'level': 'WARNING',
    },
}

# Django Allauth para testing
ACCOUNT_EMAIL_VERIFICATION = 'none'

# Security settings relajadas para testing
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Configuración específica para testing
ECOMMERCE_SETTINGS.update({
    'DEBUG_MODE': True,
    'MOCK_PAYMENTS': True,
    'SEED_DATA': False,
    'TESTING': True,
})

# Configuración de pytest
PYTEST_SETTINGS = {
    'REUSE_DB': True,
    'NOMIGRATIONS': True,
}

print("🧪 Tech Ecommerce - Modo Testing Activado")
