import os
import re

from .base import *

DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'stura-md.de').split(',')

MIDDLEWARE += [
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

# Database

if os.environ.get('DATABASE_URL'):
    match = re.search(r'^(\w+)://(\w+):(\w+)@([^:]+):(\d+)/(\w+)$', os.environ['DATABASE_URL'])
    os.environ['DB_USER'] = match.group(2)
    os.environ['DB_PASSWORD'] = match.group(3)
    os.environ['DB_HOST'] = match.group(4)
    os.environ['DB_PORT'] = match.group(5)
    os.environ['DB_NAME'] = match.group(6)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': os.environ['DB_HOST'],
        'PORT': os.environ['DB_PORT'],
    }
}


# E-Mail

EMAIL_USE_TLS = True

EMAIL_HOST = os.environ['EMAIL_HOST']

EMAIL_PORT = os.environ['EMAIL_PORT']

EMAIL_HOST_USER = os.environ['EMAIL_USER']

EMAIL_HOST_PASSWORD = os.environ['EMAIL_PASSWORD']

DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_EMAIL', 'no-reply@stura-md.de')


# Static files

STATIC_ROOT = BASE_DIR / 'static'


# Security

SECURE_HSTS_SECONDS = 31536000

SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SECURE_HSTS_PRELOAD = True

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True
