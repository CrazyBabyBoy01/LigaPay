# Это позволяет использовать celery, как только запускается проект
from .celery import app as celery_app


__all__ = ("celery_app",)
