"""
Base settings para Tech Ecommerce.
"""

import os
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Environment variables
env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, ''),
    ALLOWED_HOSTS=(list, []),
)

# Take environment variables from .env file
environ.Env.read_env(BASE_DIR / '.env')

# Security Settings
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'corsheaders',
    'crispy_forms',
    'crispy_tailwind',
    'django_htmx',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'versatileimagefield',
    'django_celery_beat',
    'django_celery_results',
    'drf_spectacular',
]

LOCAL_APPS = [
    'apps.core',
    'apps.accounts',
    'apps.products',
    'apps.inventory',
    'apps.cart',
    'apps.orders',
    'apps.payments',
    'apps.shipping',
    'apps.reviews',
    'apps.wishlist',
    'apps.notifications',
    'apps.coupons',
    'apps.analytics',
    'apps.support',
    'apps.api',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors_optimized.optimized_site_context',
                'apps.core.context_processors_optimized.optimized_cart_context',
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': env('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': env('DB_NAME', default=BASE_DIR / 'db.sqlite3'),
        'USER': env('DB_USER', default=''),
        'PASSWORD': env('DB_PASSWORD', default=''),
        'HOST': env('DB_HOST', default=''),
        'PORT': env('DB_PORT', default=''),
        'CONN_MAX_AGE': 600,  # 10 minutos de conexión persistente
        'TEST': {
            'NAME': 'test_tech_ecommerce',
        }
    }
}

# Configuración alternativa para PostgreSQL (cuando esté disponible)
if env('USE_POSTGRESQL', default=False):
    DATABASES['default'].update({
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='tech_ecommerce'),
        'USER': env('DB_USER', default='postgres'),
        'PASSWORD': env('DB_PASSWORD', default=''),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
        'OPTIONS': {
            'MAX_CONNS': 20,
            'OPTIONS': {
                '-c default_transaction_isolation=read committed',
                '-c timezone=UTC',
            }
        },
    })

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache' if not env('USE_REDIS', default=False) else 'django_redis.cache.RedisCache',
        'LOCATION': 'unique-snowflake' if not env('USE_REDIS', default=False) else env('REDIS_URL', default='redis://localhost:6379/1'),
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 3,
        } if not env('USE_REDIS', default=False) else {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 20,
                'retry_on_timeout': True,
            },
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
        },
        'KEY_PREFIX': 'tech_ecommerce',
        'TIMEOUT': 300,
    },
    'sessions': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache' if not env('USE_REDIS', default=False) else 'django_redis.cache.RedisCache',
        'LOCATION': 'sessions-snowflake' if not env('USE_REDIS', default=False) else env('REDIS_URL', default='redis://localhost:6379/2'),
        'OPTIONS': {
            'MAX_ENTRIES': 500,
            'CULL_FREQUENCY': 3,
        } if not env('USE_REDIS', default=False) else {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 10,
                'retry_on_timeout': True,
            },
        },
        'KEY_PREFIX': 'session',
        'TIMEOUT': 86400,  # 24 horas
    },
    'auth': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache' if not env('USE_REDIS', default=False) else 'django_redis.cache.RedisCache',
        'LOCATION': 'auth-snowflake' if not env('USE_REDIS', default=False) else env('REDIS_URL', default='redis://localhost:6379/3'),
        'OPTIONS': {
            'MAX_ENTRIES': 200,
            'CULL_FREQUENCY': 3,
        } if not env('USE_REDIS', default=False) else {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 10,
                'retry_on_timeout': True,
            },
        },
        'KEY_PREFIX': 'auth',
        'TIMEOUT': 3600,  # 1 hora
    },
}

# Session engine optimizado
SESSION_ENGINE = 'django.contrib.sessions.backends.db' if not env('USE_REDIS', default=False) else 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default' if not env('USE_REDIS', default=False) else 'sessions'
SESSION_COOKIE_AGE = 86400  # 24 horas
SESSION_SAVE_EVERY_REQUEST = False  # Solo guardar cuando cambie

# Password validation optimizada (solo las esenciales para mejor rendimiento)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Site ID
SITE_ID = 1

# Cache settings adicionales para mejorar rendimiento
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 600  # 10 minutos
CACHE_MIDDLEWARE_KEY_PREFIX = 'tech_ecommerce'

# Template caching
TEMPLATE_CACHE_TIMEOUT = 3600  # 1 hora para templates estáticos

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# DRF Spectacular Settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'Tech Ecommerce API',
    'DESCRIPTION': 'API para ecommerce de tecnología',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = 'tailwind'
CRISPY_TEMPLATE_PACK = 'tailwind'

# Django Allauth
AUTHENTICATION_BACKENDS = [
    'apps.accounts.auth_backends.OptimizedAuthBackend',  # Backend optimizado primero
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Django Allauth Configuration
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'optional'  # Cambiado para mejor UX
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/logout-success/'  # Redirigir a página de logout exitoso
ACCOUNT_LOGIN_REDIRECT_URL = '/'
ACCOUNT_SIGNUP_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/'

# Configuraciones adicionales de allauth para mejor UX y rendimiento
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_LOGOUT_ON_GET = True  # Logout automático sin confirmación
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_PASSWORD_MIN_LENGTH = 8

# Optimizaciones de rendimiento para allauth
ACCOUNT_RATE_LIMITS = {
    "login_failed": "5/5m/ip",  # 5 intentos por IP cada 5 minutos
    "add_email": "5/h/user",
    "change_password": "5/m/user",
    "manage_email": "10/m/user",
    "reset_password": "20/d/ip,5/m/email",
    "reset_password_email": "20/d/ip,5/m/email",
    "confirm_email": "1/3m/key",
}

# Mensajes personalizados
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[Tech Ecommerce] '
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'  # Usar HTTPS en producción

# Formularios personalizados (opcional)
ACCOUNT_FORMS = {
    'login': 'allauth.account.forms.LoginForm',
    'signup': 'allauth.account.forms.SignupForm',
    'reset_password': 'allauth.account.forms.ResetPasswordForm',
}

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@techecommerce.com')

# Celery Configuration
CELERY_BROKER_URL = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': env('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
    },
}

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# VersatileImageField
VERSATILEIMAGEFIELD_SETTINGS = {
    'cache_length': 2592000,
    'cache_name': 'versatileimagefield_cache',
    'jpeg_resize_quality': 70,
    'sized_directory_name': '__sized__',
    'filtered_directory_name': '__filtered__',
    'placeholder_directory_name': '__placeholder__',
    'create_images_on_demand': True,
}

# App-specific settings
ECOMMERCE_SETTINGS = {
    'CURRENCY': 'COP',
    'CURRENCY_SYMBOL': '$',
    'TAX_RATE': 0.19,  # 19% IVA en Colombia
    'FREE_SHIPPING_THRESHOLD': 100000,  # $100,000 COP
    'MAX_CART_ITEMS': 100,
    'PRODUCT_IMAGES_MAX': 10,
    'REVIEW_MODERATION': True,
    'WISHLIST_MAX_ITEMS': 50,
}

# Payment Settings
PAYMENT_SETTINGS = {
    'CURRENCY': 'COP',
    'CURRENCY_CODE': 'COP',
    'SUPPORTED_CURRENCIES': ['COP', 'USD'],
    'DEFAULT_PAYMENT_METHOD': 'stripe',
    'REQUIRE_BILLING_ADDRESS': False,
    'ENABLE_SAVED_CARDS': False,  # Fase futura
}

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY', default='')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY', default='')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET', default='')
STRIPE_LIVE_MODE = env('STRIPE_LIVE_MODE', default=False)

# PayPal Configuration  
PAYPAL_CLIENT_ID = env('PAYPAL_CLIENT_ID', default='')
PAYPAL_CLIENT_SECRET = env('PAYPAL_CLIENT_SECRET', default='')
PAYPAL_MODE = env('PAYPAL_MODE', default='sandbox')  # 'sandbox' or 'live'

# Site Configuration
SITE_URL = env('SITE_URL', default='http://localhost:8000')

# Email Settings for Order Notifications
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='Tech Ecommerce <noreply@techecommerce.com>')

# Order Settings
ORDER_SETTINGS = {
    'ORDER_NUMBER_PREFIX': 'TE',
    'ORDER_NUMBER_LENGTH': 8,
    'AUTO_CAPTURE_PAYMENT': True,
    'PAYMENT_TIMEOUT_MINUTES': 30,
    'INVENTORY_HOLD_MINUTES': 15,
    'ALLOW_GUEST_CHECKOUT': True,
    'REQUIRE_PHONE_NUMBER': True,
    'ORDER_STATUS_CHOICES': [
        ('pending', 'Pending Payment'),
        ('paid', 'Payment Confirmed'),
        ('processing', 'Order Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ],
    'PAYMENT_STATUS_CHOICES': [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ],
}
