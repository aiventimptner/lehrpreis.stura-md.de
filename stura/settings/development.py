from .common import *  # noqa

DEBUG = True

ALLOWED_HOSTS = ['*']


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}


# Security

SESSION_COOKIE_SECURE = False

CSRF_COOKIE_SECURE = False
