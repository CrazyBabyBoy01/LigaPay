from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse


def send_verification_email(self):
    """
    Отправляет пользователю письмо для подтверждения email.

    Формирует ссылку с кодом подтверждения, включает её в сообщение
    и отправляет письмо на текущий адрес пользователя.
    """
    link = reverse(
        'users:email_verification',
        kwargs={'email': self.user.email, 'code': self.code},
    )
    verification_link = f'{settings.DOMAIN_NAME}{link}'
    subject = f'Подтверждение учетной записи для {self.user.username}'
    message = (
        f'Для подтверждения учетной записи для {self.user.email} '
        f'перейдите по ссылке: {verification_link}'
    )
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[self.user.email],
        fail_silently=False,
    )
