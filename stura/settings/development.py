import os

from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# E-Mail

EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')

EMAIL_PORT = os.getenv('EMAIL_PORT', 1025)

EMAIL_HOST_USER = os.getenv('EMAIL_USER')

EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD')
