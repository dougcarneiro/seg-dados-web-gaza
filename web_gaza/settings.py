import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')


def require_env(key):
    value = os.environ.get(key)
    if value is None or value == '':
        raise ValueError(f'Missing required environment variable: {key}')
    return value


def env_bool(key, default=None):
    raw = os.environ.get(key)
    if raw is None or raw == '':
        if default is None:
            raise ValueError(f'Missing required environment variable: {key}')
        return default
    return raw.lower() in ('1', 'true', 'yes', 'on')


def env_int(key, default=None):
    raw = os.environ.get(key)
    if raw is None or raw == '':
        if default is None:
            raise ValueError(f'Missing required environment variable: {key}')
        return default
    return int(raw)


SECRET_KEY = require_env('SECRET_KEY')
DEBUG = env_bool('DEBUG')
ALLOWED_HOSTS = [h.strip() for h in require_env('ALLOWED_HOSTS').split(',') if h.strip()]
LANGUAGE_CODE = require_env('LANGUAGE_CODE')
TIME_ZONE = require_env('TIME_ZONE')

_sqlite_rel = require_env('SQLITE_PATH')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / _sqlite_rel if not os.path.isabs(_sqlite_rel) else Path(_sqlite_rel),
    }
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'refugees',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'web_gaza.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'web_gaza.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12},
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    {'NAME': 'refugees.validators.ForbiddenPasswordListValidator'},
]

AUTH_USER_MODEL = 'refugees.User'

HIBP_ENABLED = env_bool('HIBP_ENABLED', default=False)

EMAIL_BACKEND = require_env('EMAIL_BACKEND')
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = env_int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = require_env('DEFAULT_FROM_EMAIL')

USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/profile/'
LOGOUT_REDIRECT_URL = '/'
