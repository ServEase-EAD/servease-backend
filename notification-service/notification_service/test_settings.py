"""
Test settings for notification service.
Inherits from base settings but removes dependencies that cause test issues.
"""
from notification_service.settings import *

# Remove daphne and channels from INSTALLED_APPS for testing
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'app_notifications',
]

# Use in-memory database for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable channel layers for testing
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

# Disable password validation for tests
AUTH_PASSWORD_VALIDATORS = []

# Use simple password hasher for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
