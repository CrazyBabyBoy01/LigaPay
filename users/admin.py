from django.contrib import admin

from users.models import EmailVerification, User


# Register your models here.
admin.site.register(User)


class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ("code", "user", "expiration")
    fields = ("code", "user", "expiration", "created")
    readonly_fields = ("created",)


admin.site.register(EmailVerification,EmailVerificationAdmin)
