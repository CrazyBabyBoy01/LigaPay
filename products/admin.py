from django.contrib import admin

from .models import (
    AccountService,
    BattlePassService,
    BoostService,
    Category,
    DonationService,
    OtherService,
    QualificationService,
    RPService,
    TrainingService,
)


class BaseServiceAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title",)


# Регистрируем все модели с этим классом
admin.site.register(RPService, BaseServiceAdmin)
admin.site.register(AccountService, BaseServiceAdmin)
admin.site.register(DonationService, BaseServiceAdmin)
admin.site.register(BoostService, BaseServiceAdmin)
admin.site.register(TrainingService, BaseServiceAdmin)
admin.site.register(BattlePassService, BaseServiceAdmin)
admin.site.register(OtherService, BaseServiceAdmin)
admin.site.register(QualificationService, BaseServiceAdmin)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
