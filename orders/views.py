from django.apps import apps
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView
from products.forms import PurchaseForm
from products.models import (
    AccountService,
    BattlePassService,
    BoostService,
    DonationService,
    GeneralService,
    OtherService,
    QualificationService,
    RPService,
    ServerBasedService,
    TrainingService,
)

from .models import Order


class CreateOrderView(LoginRequiredMixin, View):
    """Создание заказа и попытка оплаты"""

    def post(self, request, model_name, product_id):
        form = PurchaseForm(request.POST)

        if not form.is_valid():
            messages.error(request, "Некорректные данные!")
            return redirect("users:profile", pk=request.user.pk)

        # Получаем данные из формы
        amount = form.cleaned_data["amount"]
        price = form.cleaned_data["price"]
        player_id = form.cleaned_data["player_id"]
        payment_method = form.cleaned_data["payment_method"]

        # Получаем товар
        model = apps.get_model("products", model_name)
        if not model:
            messages.error(request, "Некорректная категория товара!")
            return redirect("users:profile", pk=request.user.pk)

        try:
            product = model.objects.get(id=product_id)
        except model.DoesNotExist:
            messages.error(request, "Товар не найден!")
            return redirect("users:profile", pk=request.user.pk)

        # Вычисляем финальную стоимость (цена за штуку * количество)
        total_price = product.price * amount

        # Создаём заказ
        order = Order.objects.create(
            user=request.user,
            seller=product.seller,
            content_type=ContentType.objects.get_for_model(product),
            object_id=product.id,
            price=total_price,  # Теперь цена зависит от количества!
            description=product.description,
        )

        # Пытаемся оплатить
        if order.process_payment():
            order.save()
            messages.success(request, f"Вы купили {amount} шт. товара! 🎉")
        else:
            messages.error(request, "Недостаточно средств!")

        return redirect("users:profile", pk=request.user.pk)


class OrderListView(LoginRequiredMixin, ListView):
    """Вывод списка заказов пользователя"""

    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        """Фильтруем заказы только для текущего пользователя"""
        return Order.objects.filter(user=self.request.user).order_by("-created_at")

class SaleListView(LoginRequiredMixin, ListView):
    """Вывод списка продаж пользователя"""
    model = Order
    template_name = "orders/sale_list.html"
    context_object_name = "sales"

    def get_queryset(self):
        """Фильтруем заказы, где текущий пользователь является продавцом"""
        return Order.objects.filter(seller=self.request.user).order_by("-created_at")
