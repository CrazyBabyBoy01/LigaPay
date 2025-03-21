from decimal import Decimal

from common.views import ContextMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from wallet.models import Wallet


class DepositView(ContextMixin, LoginRequiredMixin, View):
    """Обрабатывает пополнение баланса"""

    title = "Пополнение кошелька"
    template_name = "wallet/deposit.html"

    def get(self, request):
        """Показываем форму"""
        return render(request, self.template_name)

    def post(self, request):
        """Обрабатываем пополнение"""
        amount = request.POST.get("amount")

        try:
            amount = Decimal(amount)
            if amount <= 0:
                raise ValidationError("Сумма пополнения должна быть больше 0.")

            request.user.wallet.deposit(amount)  # Вызываем метод кошелька
        except (ValidationError, ValueError) as e:
            return render(request, self.template_name, {"error": str(e)})

        return redirect(
            reverse("users:profile", kwargs={"pk": request.user.pk})
        )  # После пополнения возвращаем в профиль
