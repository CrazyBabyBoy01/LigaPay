import os

from .base import *


# Режим разработки
DEBUG = True

ALLOWED_HOSTS = ['*']

DOMAIN_NAME = 'http://localhost:8000'


# -------------------------------
# DATABASES (локальный Postgres)
# -------------------------------

POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': POSTGRES_HOST,
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
        'OPTIONS': {
            'options': '-c client_encoding=UTF8',
        },
    }
}

# -------------------------------
# REDIS (локальный)
# -------------------------------
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')

# Кэш
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    }
}

# Channels (локальный redis)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(REDIS_HOST, int(REDIS_PORT))],
        },
    },
}

# Celery (локальный redis)
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# Debug toolbar allowed
INTERNAL_IPS = ['127.0.0.1']
