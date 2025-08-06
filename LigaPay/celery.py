import os

from celery import Celery


# Укажите название проекта
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LigaPay.settings')

app = Celery('LigaPay')

app.conf.update(
    worker_pool='solo',  # или попробуйте eventlet или gevent
)

# Загрузите конфигурацию из settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически обнаруживает задачи в приложениях
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
