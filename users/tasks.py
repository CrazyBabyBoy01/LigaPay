import uuid
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.utils.timezone import now

from users.models import EmailVerification, User


@shared_task
def send_email_verification(user_identifier):
    """
    Отправляет email-подтверждение для пользователя.
    user_identifier может быть числовым id или email.
    """
    try:
        # Определяем, что передано: id или email
        if isinstance(user_identifier, int):
            user = User.objects.get(id=user_identifier)
        elif isinstance(user_identifier, str):
            user = User.objects.get(email=user_identifier)
        else:
            raise ValueError('Invalid user identifier type')

        # Создаём запись подтверждения email
        expiration = now() + timedelta(hours=48)
        record = EmailVerification.objects.create(code=uuid.uuid4(), user=user, expiration=expiration)
        record.send_verification_email()
    except ObjectDoesNotExist as err:
        raise ValueError('User matching query does not exist') from err


@shared_task
def send_reset_email(subject, message, recipient_list, html_message=None):
    """
    Отправляет email с помощью Celery.
    """
    return send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
        html_message=html_message,
    )
