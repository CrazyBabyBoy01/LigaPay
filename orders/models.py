from decimal import Decimal

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from products.models import BaseService  # Импортируем базовую модель товаров
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
    price = models.DecimalField(max_digits=10,default=0.0, decimal_places=2, verbose_name="Цена на момент покупки")
    description = models.TextField(
        default="Описание недоступно", verbose_name="Описание заказа"
    )  # ✔ Это текст, здесь все ОК
    product = GenericForeignKey("content_type", "object_id")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="Статус заказа")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Связываем с моделью пользователя
        on_delete=models.SET_NULL,  # Если продавец удалится, заказ останется, но без продавца
        null=True,
        blank=True,
        related_name="sales",  # Позволит найти все продажи продавца через user.sales.all()
        verbose_name="Продавец",
    )

    def process_payment(self):
        """Метод обработки оплаты"""

        # Получаем кошелек покупателя
        buyer_wallet = Wallet.objects.get(user=self.user)

        # Проверяем, есть ли продавец (на всякий случай)
        if not self.seller:
            print("Ошибка: у товара нет продавца.")
            return False

        try:
            # Получаем кошелек продавца
            seller_wallet = Wallet.objects.get(user=self.seller)
        except Wallet.DoesNotExist:
            print("Ошибка: у продавца нет кошелька.")
            return False

        # Проверяем, хватает ли у покупателя денег
        if buyer_wallet.balance >= self.price:
            # Используем "атомарную" транзакцию, чтобы избежать ошибок при переводе
            with transaction.atomic():
                # 1. Списываем деньги у покупателя
                buyer_wallet.withdraw(self.price)

                # 2. Начисляем деньги продавцу
                seller_wallet.deposit(self.price)

                # 3. Меняем статус заказа на "оплачено"
                self.status = "paid"
                self.save()

                # 4. Если товар одноразовый (например, аккаунт), делаем его недоступным
                if hasattr(self.product, "is_active"):
                    self.product.is_active = False
                    self.product.save()

            print(f"Покупка успешна! {self.price}₽ переведены от {self.user.username} к {self.seller.username}.")
            return True  # Возвращаем True – всё прошло успешно

    def __str__(self):
        return f"Заказ {self.id} - {self.product} ({self.status})"
