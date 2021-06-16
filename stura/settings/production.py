from .common import *  # noqa

DEBUG = False

ALLOWED_HOSTS = [
    'lehrpreis.stura-md.de',
    'www.lehrpreis.stura-md.de',
    'stura-md.de',
    'www.stura-md.de',
] + os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

MIDDLEWARE += [
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ADMINS = [('Verwaltung', 'verwaltung@stura-md.de'), ('Technik', 'technik@stura-md.de')]


# Security

SECURE_HSTS_SECONDS = 31536000

SECURE_HSTS_PRELOAD = True

SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SECURE_SSL_REDIRECT = False  # Nginx used as reverse proxy

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True
