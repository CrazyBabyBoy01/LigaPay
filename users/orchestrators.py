import os
from django.conf import settings

from users.tasks import send_email_verification


def send_verification_email(user_identifier) -> None:
    """
    Оркестратор отправки email-подтверждения.

    - В тестах (eager) → синхронно
    - В dev/prod → через Celery
    """
    if getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', False):
        send_email_verification(user_identifier)
    else:
        send_email_verification.delay(user_identifier)
