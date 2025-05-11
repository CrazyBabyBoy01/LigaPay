from decimal import Decimal

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from wallet.models import Wallet  # Импортируем кошелек пользователя


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Ожидание оплаты"),
        ("paid", "Оплачено"),
        ("canceled", "Отменено"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders", verbose_name="Покупатель"
    )

    # Поля для GenericForeignKey
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, default=0.0, decimal_places=2, verbose_name="Цена на момент покупки")
    description = models.TextField(
        default="Описание недоступно", verbose_name="Описание заказа"
    )  # ✔ Это текст, здесь все ОК
    product = GenericForeignKey("content_type", "object_id")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="Статус заказа")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    amount = models.PositiveIntegerField()
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Связываем с моделью пользователя
        on_delete=models.SET_NULL,  # Если продавец удалится, заказ останется, но без продавца
        null=True,
        blank=True,
        related_name="sales",  # Позволит найти все продажи продавца через user.sales.all()
        verbose_name="Продавец",
    )

    def process_payment(self):
        """Метод обработки оплаты с учетом количества товара"""

        try:
            buyer_wallet = Wallet.objects.get(user=self.user)  # Кошелек покупателя
            seller_wallet = Wallet.objects.get(user=self.seller)  # Кошелек продавца
        except Wallet.DoesNotExist:
            print("Ошибка: у одного из пользователей нет кошелька.")
            return False

        total_price = self.price * self.amount  # Общая стоимость заказа

        if buyer_wallet.balance < total_price:
            print("Ошибка: недостаточно средств.")
            return False  # Покупка невозможна

        with transaction.atomic():
            # 1. Списываем деньги у покупателя
            buyer_wallet.balance -= total_price
            buyer_wallet.save()

            # 2. Зачисляем деньги продавцу
            seller_wallet.balance += total_price
            seller_wallet.save()

            # 4. Меняем статус заказа на "оплачено"
            self.status = "paid"
            self.save()

        print(f"Покупка успешна! {total_price}₽ переведены от {self.user.username} к {self.seller.username}.")
        return True  # Покупка успешно завершена

    def __str__(self):
        return f"Заказ {self.id} - {self.product} ({self.status})"
