from django.db import models

from users.models import User


# Create your models here.
class SkinsOrder(models.Model):
    SERVER_CHOICES = [
        ('nordic', 'EU Nordic & East'),
        ('west', 'EU West'),
        ('japan', 'Japan'),
        ('north', 'Latin America North'),
        ('south', 'Latin America South'),
        ('namerica', 'North America'),
        ('russia', 'Russia'),
        ('turkey', 'Turkey'),
        ('other', 'Другой сервер'),
    ]
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='skins_orders',
        verbose_name='Пользователь',
    )

    char_name = models.CharField(max_length=50, verbose_name='Персонаж', blank=True)
    skin_name = models.CharField(max_length=50, verbose_name='Образ', blank=True)
    price_char = models.IntegerField(blank=True, null=True, verbose_name='Цена персонажа')
    price_skin = models.IntegerField(blank=True, null=True, verbose_name='Цена образа')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    server = models.CharField(
        max_length=20, choices=SERVER_CHOICES, default='west', verbose_name='Сервер'
    )
    account_name = models.CharField(
        max_length=50, verbose_name='Никнейм аккаунта', default='default_name'
    )

    class Meta:
        verbose_name = 'Скины и персонажи'
        verbose_name_plural = 'Скины и персонажи'

    def __str__(self):
        if self.char_name:
            return f'Заказ персонажа {self.char_name}'
        if self.skin_name:
            return f'Заказ образа {self.skin_name}'
