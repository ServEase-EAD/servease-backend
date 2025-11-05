from pathlib import Path
import os
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-f7loa%13hw3bxx*_4mi1bej$vt(qs59zwet3kmew1a6je3-rgo')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')

# ----------------------------------------------------------------------
# Application Definition
# ----------------------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'rest_framework',
    'corsheaders',

    # Local apps
    'appointments',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # ✅ Must be very top
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'appointment_service.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'appointment_service.wsgi.application'

# ----------------------------------------------------------------------
# Database
# ----------------------------------------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('APPOINTMENT_DB_NAME', default='servease_appointments'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {'sslmode': 'require'},
    }
}

# ----------------------------------------------------------------------
# Password validation
# ----------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ----------------------------------------------------------------------
# Internationalization
# ----------------------------------------------------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ----------------------------------------------------------------------
# Static files
# ----------------------------------------------------------------------

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ----------------------------------------------------------------------
# Django REST Framework
# ----------------------------------------------------------------------

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'common.authentication.StatelessJWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# ----------------------------------------------------------------------
# ✅ CORS Configuration
# ----------------------------------------------------------------------

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Frontend (Vite)
    "http://localhost",       # Nginx Gateway
]

CORS_ALLOW_HEADERS = [
    "authorization",
    "content-type",
    "accept",
    "origin",
    "x-requested-with",
    "x-csrftoken",
]

CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]

# ----------------------------------------------------------------------
# Service URLs (Microservice Communication)
# ----------------------------------------------------------------------

SERVICE_URLS = {
    'CUSTOMER_SERVICE': config('CUSTOMER_SERVICE_URL', default='http://customer-service:8002'),
    'EMPLOYEE_SERVICE': config('EMPLOYEE_SERVICE_URL', default='http://employee-service:8003'),
    'VEHICLE_SERVICE': config('VEHICLE_SERVICE_URL', default='http://vehicleandproject-service:8004'),
    'APPOINTMENT_SERVICE': config('APPOINTMENT_SERVICE_URL', default='http://appointment-service:8005'),
    'NOTIFICATION_SERVICE': config('NOTIFICATION_SERVICE_URL', default='http://notification-service:8006'),
    'USER_SERVICE': config('USER_SERVICE_URL', default='http://authentication-service:8001'),
    'CHATBOT_SERVICE': config('CHATBOT_SERVICE_URL', default='http://chatbot-service:8008'),
}

# ----------------------------------------------------------------------
# Redis Cache Configuration
# ----------------------------------------------------------------------

REDIS_HOST = config('REDIS_HOST', default='redis')
REDIS_PORT = config('REDIS_PORT', default='6379')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'appointment_service',
        'TIMEOUT': 300,
    }
}

# ----------------------------------------------------------------------
# JWT Configuration
# ----------------------------------------------------------------------

SIMPLE_JWT = {
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",
    "USER_ID_FIELD": "user_id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ----------------------------------------------------------------------
# Appointment Service Config
# ----------------------------------------------------------------------

MAX_CONCURRENT_APPOINTMENTS = config('MAX_CONCURRENT_APPOINTMENTS', default=3, cast=int)
DEFAULT_APPOINTMENT_DURATION = config('DEFAULT_APPOINTMENT_DURATION', default=60, cast=int)
