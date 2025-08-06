from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from users.models import EmailVerification, User


# Register your models here.
admin.site.register(User)


class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('code', 'user', 'expiration')
    fields = ('code', 'user', 'expiration', 'created')
    readonly_fields = ('created',)


admin.site.register(EmailVerification, EmailVerificationAdmin)


# ✅ Кастомная форма создания пользователя
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')


# ✅ Кастомная форма изменения пользователя
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'image', 'is_verified_email', 'last_activity')


'Отображение баланса в админке для юзера'


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('username', 'email', 'is_staff', 'display_balance')
    fieldsets = (
        (
            None,
            {'fields': ('username', 'email', 'password', 'image', 'is_verified_email', 'last_activity')},
        ),
        (
            'Permissions',
            {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active'),
            },
        ),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

    def display_balance(self, obj):
        return obj.wallet.balance if hasattr(obj, 'wallet') else 'Нет кошелька'

    display_balance.short_description = 'Баланс'  # Название колонки в админке


admin.site.unregister(User)  # Убираем стандартное отображение User
admin.site.register(User, CustomUserAdmin)  # Регистрируем кастомную админку
