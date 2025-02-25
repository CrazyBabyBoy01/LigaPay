from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from wallet.models import Wallet

from users.models import EmailVerification, User


# Register your models here.
admin.site.register(User)


class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ("code", "user", "expiration")
    fields = ("code", "user", "expiration", "created")
    readonly_fields = ("created",)


admin.site.register(EmailVerification, EmailVerificationAdmin)


"Отображение баланса в админке для юзера"


class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "is_staff", "display_balance")

    def display_balance(self, obj):
        return obj.wallet.balance if hasattr(obj, "wallet") else "Нет кошелька"

    display_balance.short_description = "Баланс"  # Название колонки в админке


admin.site.unregister(User)  # Убираем стандартное отображение User
admin.site.register(User, CustomUserAdmin)  # Регистрируем кастомную админку
