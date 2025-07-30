import json
import os
from decimal import Decimal

from django import forms
from django.conf import settings
from wallet.models import Wallet

from store.models import SkinsOrder


class SkinsOrderForm(forms.ModelForm):
    char_name = forms.CharField(widget=forms.TextInput(attrs={"class": "char1name"}), required=False)

    skin_name = forms.CharField(widget=forms.TextInput(attrs={"class": "skin1name"}), required=False)

    server = forms.ChoiceField(
        choices=SkinsOrder._meta.get_field("server").choices,
        widget=forms.Select(attrs={"class": "server1"}),
    )
    account_name = forms.CharField(widget=forms.TextInput(attrs={"class": "account_name1"}))

    price_char = forms.IntegerField(required=False)
    price_skin = forms.IntegerField(required=False)

    class Meta:
        model = SkinsOrder
        fields = {
            "char_name",
            "skin_name",
            "price_char",
            "price_skin",
            "server",
            "account_name",
        }

    def clean(self):
        cleaned_data = super().clean()
        user = self.request.user
        cleaned_data["user"] = user  # сохраняем пользователя в заказ

        try:
            wallet = Wallet.objects.get(user=user)
        except Wallet.DoesNotExist:
            raise forms.ValidationError("У вас нет кошелька. Обратитесь в поддержку.")

        # Работаем с персонажем
        if cleaned_data.get("char_name"):
            json_path = os.path.join(settings.BASE_DIR, "static", "deps", "chars", "assets", "name2price.json")
            with open(json_path, encoding="utf-8") as file:
                json_data = json.load(file)
            price = Decimal(json_data[cleaned_data["char_name"]])
            cleaned_data["price_char"] = price

            if wallet.balance < price:
                raise forms.ValidationError("Недостаточно средств для покупки персонажа.")

        # Работаем с образом
        if cleaned_data.get("skin_name"):
            json_path = os.path.join(settings.BASE_DIR, "static", "deps", "chars", "assets", "skins2price.json")
            with open(json_path, encoding="utf-8") as file:
                json_data = json.load(file)
            price = Decimal(json_data[cleaned_data["skin_name"]])
            cleaned_data["price_skin"] = price

            if wallet.balance < price:
                raise forms.ValidationError("Недостаточно средств для покупки образа.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.request.user

        # ➕ Явно устанавливаем цены из cleaned_data
        instance.price_skin = self.cleaned_data.get("price_skin")
        instance.price_char = self.cleaned_data.get("price_char")

        amount = instance.price_skin or instance.price_char
        print("==> Итоговая сумма к списанию:", amount)

        wallet = Wallet.objects.get(user=self.request.user)
        wallet.withdraw(amount)

        if commit:
            instance.save()
        return instance
