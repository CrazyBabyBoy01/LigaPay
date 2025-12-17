import os

from django.db.backends.signals import connection_created

from .base import *


DEBUG = False

# Тесты не должны падать из-за ALLOWED_HOSTS
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

# -------------------------------
# База данных для тестов
# Django сам создаёт test_ база
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
    }
}

# -------------------------------
# Channels без Redis в тестах!
# -------------------------------
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# -------------------------------
# Celery — синхронный режим
# -------------------------------
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache+memory://'

# -------------------------------
# Кэш — отключён (локальный словарь)
# -------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# -------------------------------
# Email — консольный backend
# -------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# -------------------------------
# Captcha — отключаем проверки
# -------------------------------
NOCAPTCHA = True

# -------------------------------
# Отключаем FK check для тестов
# (у тебя это уже было — переносим сюда)
# -------------------------------


def disable_fk_checks(sender, connection, **kwargs):
    if connection.vendor == 'postgresql':
        with connection.cursor() as cursor:
            cursor.execute('SET session_replication_role = replica;')


connection_created.connect(disable_fk_checks)
