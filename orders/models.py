from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидание оплаты'),
        ('paid', 'Оплачено'),
        ('canceled', 'Отменено'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Покупатель',
    )

    # Поля для GenericForeignKey
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    price = models.DecimalField(
        max_digits=10, default=0.0, decimal_places=2, verbose_name='Цена на момент покупки'
    )
    description = models.TextField(
        default='Описание недоступно', verbose_name='Описание заказа'
    )  # ✔ Это текст, здесь все ОК
    product = GenericForeignKey('content_type', 'object_id')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус заказа'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    amount = models.PositiveIntegerField()
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Связываем с моделью пользователя
        on_delete=models.SET_NULL,  # Если продавец удалится, заказ останется, но без продавца
        null=True,
        blank=True,
        related_name='sales',  # Позволит найти все продажи продавца через user.sales.all()
        verbose_name='Продавец',
    )

    def __str__(self):
        return f'Заказ {self.id} - {self.product} ({self.status})'

    def hold_payment(self):
        from .services import OrderService

        return OrderService.hold_payment(self)

    def process_payment(self):
        """Метод обработки оплаты с учетом количества товара"""

        from .services import OrderService

        return OrderService.process_payment(self)

    def refund(self):
        """Метод обработки оплаты с учетом количества товара"""

        from .services import OrderService

        return OrderService.refund(self)


# Модель для отзывов
class Review(models.Model):
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name='review', verbose_name='Заказ'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_written',
        verbose_name='Автор',
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_received',
        verbose_name='Продавец',
    )
    rating = models.PositiveSmallIntegerField(
        verbose_name='Оценка (1-5)', validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(verbose_name='Комментарий', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отзыва')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'Отзыв от {self.author.username} продавцу {self.seller.username}'
