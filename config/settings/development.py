"""
Development settings para Tech Ecommerce.
"""

from .base import *

# Debug settings
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', 'testserver']

# Configuraciones de seguridad para desarrollo
# NOTA: Estas configuraciones son para desarrollo local.
# En producción se deben usar valores más seguros.
SECURE_HSTS_SECONDS = 0  # Deshabilitado en desarrollo
SECURE_SSL_REDIRECT = False  # No forzar HTTPS en desarrollo
SESSION_COOKIE_SECURE = False  # Permitir cookies sin HTTPS en desarrollo
CSRF_COOKIE_SECURE = False  # Permitir CSRF sin HTTPS en desarrollo
SECURE_BROWSER_XSS_FILTER = True  # Siempre habilitado
SECURE_CONTENT_TYPE_NOSNIFF = True  # Siempre habilitado

# Database para desarrollo (SQLite optimizado)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 30,
        },
        'CONN_MAX_AGE': 60,  # Reutilizar conexiones
    }
}

# OPTIMIZACIONES DE RENDIMIENTO PARA DESARROLLO
# Password hashers rápidos para desarrollo (NO usar en producción)
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',  # Muy rápido para desarrollo
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',  # Fallback
]

# Cache con fallback a LocMem (Redis opcional)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 300,  # 5 minutos
        'OPTIONS': {
            'MAX_ENTRIES': 2000,  # Aumentado para mejor rendimiento
        }
    }
}

# Cache para sesiones (mejora rendimiento de login)
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'

# Optimizaciones adicionales de rendimiento
CONN_MAX_AGE = 60  # Reutilizar conexiones DB por 60 segundos

# Email backend para desarrollo
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Static files en desarrollo
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Media files en desarrollo
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Django Debug Toolbar - TEMPORALMENTE DESACTIVADO
DEBUG_TOOLBAR_ENABLED = False
if DEBUG and DEBUG_TOOLBAR_ENABLED:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]
    
    DEBUG_TOOLBAR_CONFIG = {
        'DISABLE_PANELS': [
            'debug_toolbar.panels.redirects.RedirectsPanel',
        ],
        'SHOW_TEMPLATE_CONTEXT': True,
    }

# Django Extensions
INSTALLED_APPS += ['django_extensions']

# Disable CSRF in development for easier API testing
# CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']

# Logging más verboso en desarrollo
LOGGING['loggers']['django']['level'] = 'DEBUG'
LOGGING['loggers']['apps'] = {
    'handlers': ['console'],
    'level': 'DEBUG',
    'propagate': False,
}

# Celery en desarrollo - usar siempre eager
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Django Allauth en desarrollo
ACCOUNT_EMAIL_VERIFICATION = 'none'  # No verificación de email en desarrollo

# CORS más permisivo en desarrollo
CORS_ALLOW_ALL_ORIGINS = True

# Security settings para desarrollo
# En desarrollo, mantenemos configuraciones relajadas pero comentamos las opciones
# SECURE_SSL_REDIRECT = False  # Solo HTTP en desarrollo
# SESSION_COOKIE_SECURE = False  # No HTTPS en desarrollo  
# CSRF_COOKIE_SECURE = False  # No HTTPS en desarrollo
# SECURE_HSTS_SECONDS = 0  # Deshabilitado en desarrollo

# Configuraciones básicas que sí aplicamos en desarrollo
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Performance settings para desarrollo
# DATABASES['default']['OPTIONS'] = {
#     'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
#     'charset': 'utf8mb4',
# }

# Configuración específica para desarrollo
ECOMMERCE_SETTINGS.update({
    'DEBUG_MODE': True,
    'MOCK_PAYMENTS': True,
    'SEED_DATA': True,
})

# ========================================
# OPTIMIZACIONES ADICIONALES DE RENDIMIENTO
# ========================================

# LOGGING DETALLADO PARA CONSOLA DEL SERVIDOR
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console_colored': {
            'format': '🌐 {levelname} | {asctime} | {name} | {message}',
            'style': '{',
            'datefmt': '%H:%M:%S',
        },
        'console_requests': {
            'format': '🔥 {levelname} | {asctime} | {message}',
            'style': '{',
            'datefmt': '%H:%M:%S',
        },
        'console_sql': {
            'format': '🗄️ SQL | {asctime} | {message}',
            'style': '{',
            'datefmt': '%H:%M:%S',
        },
        'console_errors': {
            'format': '❌ ERROR | {asctime} | {name} | {message}',
            'style': '{',
            'datefmt': '%H:%M:%S',
        },
        'file_detailed': {
            'format': '{levelname} {asctime} [{name}] {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console_main': {
            'class': 'logging.StreamHandler',
            'formatter': 'console_colored',
            'level': 'INFO',
        },
        'console_requests': {
            'class': 'logging.StreamHandler',
            'formatter': 'console_requests',
            'level': 'INFO',
        },
        'console_sql': {
            'class': 'logging.StreamHandler',
            'formatter': 'console_sql',
            'level': 'DEBUG',
        },
        'console_errors': {
            'class': 'logging.StreamHandler',
            'formatter': 'console_errors',
            'level': 'ERROR',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'development.log',
            'formatter': 'file_detailed',
            'level': 'DEBUG',
        },
        'error_file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'errors.log',
            'formatter': 'file_detailed',
            'level': 'ERROR',
        },
    },
    'root': {
        'handlers': ['console_main', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django.request': {
            'handlers': ['console_requests', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console_requests', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console_sql', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console_errors', 'file', 'error_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'apps.core.middleware.logging': {
            'handlers': ['console_main', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'accounts': {
            'handlers': ['console_main', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'core': {
            'handlers': ['console_main', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'cart': {
            'handlers': ['console_main', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'products': {
            'handlers': ['console_main', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'orders': {
            'handlers': ['console_main', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'payments': {
            'handlers': ['console_main', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.utils.autoreload': {
            'handlers': ['console_main'],
            'level': 'WARNING',  # Solo cambios importantes de archivos
            'propagate': False,
        },
        'rest_framework_simplejwt': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Desactivar compresión de archivos estáticos en desarrollo
COMPRESS_ENABLED = False
COMPRESS_OFFLINE = False

# Template caching para desarrollo (mínimo)
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

# Session optimizada para desarrollo
SESSION_COOKIE_AGE = 3600  # 1 hora
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = False  # No guardar en cada request

# Optimizar queries de autenticación
AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# MIDDLEWARE ADICIONAL PARA LOGGING DETALLADO EN DESARROLLO
# MIDDLEWARE.insert(3, 'apps.core.middleware.simple_logging.DetailedLoggingMiddleware')  # Temporalmente deshabilitado

print("🚀 Tech Ecommerce - Modo Desarrollo con Logging Detallado Activado")
