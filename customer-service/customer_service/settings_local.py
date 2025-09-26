"""
Local development settings for customer service
Forces SQLite database for development/testing
"""

from .settings import *
import os

# Override database settings to use SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Override other settings for local development
DEBUG = True
ALLOWED_HOSTS = ['*']

# Disable CORS for local development
CORS_ALLOW_ALL_ORIGINS = True

# Simpler logging for development
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

print("Using local SQLite database for development...")
