from pathlib import Path
import os
from dotenv import load_dotenv
from os import getenv
from datetime import timedelta
from datetime import datetime, timedelta
from django.utils.timezone import localtime

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = getenv('SECRET_KEY')

DEBUG = getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = getenv("ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'base.apps.BaseConfig',
    'import_export',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'base.log.LogMiddleware',
    "base.restrict_admin_ip's.RestrictAdminMiddleware",
]

ROOT_URLCONF = 'test_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'test_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': getenv('NAME'),
        'USER': getenv('USER'),
        'PASSWORD': getenv('PASSWORD'),
        'HOST': getenv('HOST'),
        'PORT': getenv('PORT', '3306'),
    }
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = False

STATIC_ROOT = BASE_DIR/"staticfiles"

STATIC_URL = '/static/'

if not DEBUG:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

X_FRAME_OPTIONS = "DENY"

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = not DEBUG 

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "https://your-frontend.netlify.app",
]

CSRF_COOKIE_NAME = "csrftoken"
CSRF_COOKIE_SECURE = not DEBUG

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://your-frontend.netlify.app",
]
CORS_ALLOW_CREDENTIALS = True

AUTH_USER_MODEL = 'base.Teacher'

def get_midnight_expiry():
    now = datetime.now()
    midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return (midnight - now).seconds

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(seconds=get_midnight_expiry()),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),  
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True, 
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}
