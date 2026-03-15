from datetime import timedelta
from pathlib import Path

import environ

if 'BASE_DIR' not in globals():
    BASE_DIR = Path(__file__).resolve().parents[3]

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    CORS_ALLOWED_ORIGINS=(list, []),
    CSRF_TRUSTED_ORIGINS=(list, []),
    KEYCLOAK_ENABLED=(bool, False),
    KEYCLOAK_SERVER_URL=(str, ''),
    KEYCLOAK_REALM=(str, ''),
    KEYCLOAK_CLIENT_ID=(str, ''),
    KEYCLOAK_CLIENT_SECRET=(str, ''),
    KEYCLOAK_VERIFY_SSL=(bool, True),
)

environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env.str('DJANGO_SECRET_KEY')

DEBUG = env.bool('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])
KEYCLOAK_ENABLED = env.bool('KEYCLOAK_ENABLED', default=False)
KEYCLOAK_SERVER_URL = env.str('KEYCLOAK_SERVER_URL', default='').rstrip('/')
KEYCLOAK_REALM = env.str('KEYCLOAK_REALM', default='')
KEYCLOAK_CLIENT_ID = env.str('KEYCLOAK_CLIENT_ID', default='')
KEYCLOAK_CLIENT_SECRET = env.str('KEYCLOAK_CLIENT_SECRET', default='')
KEYCLOAK_VERIFY_SSL = env.bool('KEYCLOAK_VERIFY_SSL', default=True)

INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'core',
    'okr',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'core.User'
DJANGO_SUPERUSER_EMAIL = env('DJANGO_SUPERUSER_EMAIL')
DJANGO_SUPERUSER_USERNAME = env('DJANGO_SUPERUSER_USERNAME')
DJANGO_SUPERUSER_PASSWORD = env('DJANGO_SUPERUSER_PASSWORD')

default_authentication_classes = ['rest_framework_simplejwt.authentication.JWTAuthentication']
if KEYCLOAK_ENABLED:
    default_authentication_classes.insert(0, 'core.authentication.KeycloakJWTAuthentication')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': tuple(default_authentication_classes),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}
