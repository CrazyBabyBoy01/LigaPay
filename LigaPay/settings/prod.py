import os

from .base import *


# Production mode
DEBUG = False

# В проде ALLOWED_HOSTS никогда не должно быть ['*']
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

# Домен приложения
DOMAIN_NAME = os.getenv('DOMAIN_NAME', DOMAIN_NAME)

# -------------------------------
# DATABASES (Docker Postgres)
# -------------------------------
POSTGRES_HOST = 'postgres'  # имя контейнера Postgres

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': POSTGRES_HOST,
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

# -------------------------------
# REDIS (Docker Redis)
# -------------------------------
REDIS_HOST = 'redis'  # Docker-service name
REDIS_PORT = os.getenv('REDIS_PORT', '6379')

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://redis:{REDIS_PORT}/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    }
}

# Channels Redis
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('redis', int(REDIS_PORT))],
        },
    },
}

# Celery Redis
CELERY_BROKER_URL = f'redis://redis:{REDIS_PORT}/0'
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# -------------------------------
# Security for production
# -------------------------------
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = False  # включаем True, если будет HTTPS
