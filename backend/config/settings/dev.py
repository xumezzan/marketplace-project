from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# Dev-specific settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS
CORS_ALLOW_ALL_ORIGINS = True
