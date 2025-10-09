from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now


class User(AbstractUser):
    image = models.ImageField(
        upload_to='users_images/', null=True, blank=True, verbose_name='Изображение'
    )
    is_verified_email = models.BooleanField(default=False, verbose_name='Подтверждение почты')
    email = models.EmailField(unique=True, verbose_name='Почта')
    new_email = models.EmailField(null=True, blank=True, verbose_name='Новая почта')
    email_change_token = models.CharField(
        max_length=36, null=True, blank=True, verbose_name='Токен смены email'
    )
    last_activity = models.DateTimeField(null=True, blank=True, verbose_name='Когда был(а) в сети')

    def is_online(self) -> bool:
        """Проверяет, был ли пользователь активен за последние ONLINE_MINUTES минут."""
        if not self.last_activity:
            return False
        return now() - self.last_activity < timedelta(minutes=settings.USER_ONLINE_MINUTES)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class EmailVerification(models.Model):
    code = models.UUIDField(unique=True, verbose_name='Токен')
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name='Пользователь')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания токена')
    expiration = models.DateTimeField(verbose_name='Дата жизни токена')

    class Meta:
        verbose_name = 'Подтверждение почты'
        verbose_name_plural = 'Подтверждения почты'

    def __str__(self):
        return f'EmailVerification object {self.user.email}'

    def send_verification_email(self):
        from .services import send_verification_email as send_email

        send_email(self)

    def is_expired(self) -> bool:
        """Проверяет, истёк ли срок действия токена."""
        return now() >= self.expiration
