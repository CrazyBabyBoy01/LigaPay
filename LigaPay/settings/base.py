import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv


# Загружаем .env
load_dotenv(find_dotenv())

# Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parents[2]
# Основные настройки
SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = False  # По умолчанию False — dev/prod сами включат

ALLOWED_HOSTS = []

DOMAIN_NAME = os.getenv('DOMAIN_NAME', 'http://localhost:8000')

# Приложения
INSTALLED_APPS = [
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'debug_toolbar',
    'captcha',
    'widget_tweaks',
    'django_celery_beat',
    # Local apps
    'main',
    'users',
    'news',
    'products',
    'wallet',
    'orders',
    'chat',
    'store',
]

ASGI_APPLICATION = 'LigaPay.asgi.application'
WSGI_APPLICATION = 'LigaPay.wsgi.application'

# Middleware
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Debug toolbar (dev only)
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # Custom
    'users.middleware.UpdateLastActivityMiddleware',
]

ROOT_URLCONF = 'LigaPay.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'chat.context_processors.unread_message_count',
            ],
        },
    },
]


# Static/Media
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static', BASE_DIR / 'deps']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Auth
AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/users/authorization/'

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 465))
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# reCAPTCHA test keys (common for all)
RECAPTCHA_PUBLIC_KEY = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
RECAPTCHA_PRIVATE_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'

# User activity window
USER_ONLINE_MINUTES = 5

# Logging (общий)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': True,
        },
        'orders': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

FIXTURE_DIRS = [
    BASE_DIR / 'fixtures',
]

print('DEBUG =', os.getenv('DEBUG'))
print('POSTGRES_HOST =', os.getenv('POSTGRES_HOST'))
print('REDIS_HOST =', os.getenv('REDIS_HOST'))
print('DJANGO_SETTINGS_MODULE =', os.getenv('DJANGO_SETTINGS_MODULE'))
