from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.html import format_html_join

from .models import (
    AccountService,
    BattlePassService,
    BoostService,
    Category,
    DonationService,
    GeneralService,
    OtherService,
    QualificationService,
    RPService,
    ServiceImage,
    TrainingService,
)


class ServiceImageInline(GenericTabularInline):
    model = ServiceImage
    extra = 1


class BaseServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price', 'is_active', 'seller')
    list_filter = ('is_active',)
    search_fields = ('title',)


class ServiceWithImagesAdmin(BaseServiceAdmin):
    list_display = (*BaseServiceAdmin.list_display, 'display_images')
    readonly_fields = ('display_images',)
    inlines = [ServiceImageInline]

    def display_images(self, obj):
        imgs = obj.images.all()
        if not imgs:
            return '-'
        return format_html_join(
            '',
            '<img src="{}" width="100" style="margin-right: 10px;"/>',
            ((img.image.url,) for img in imgs),
        )

    display_images.short_description = 'Картинки'


# Регистрируем все модели с этим классом
admin.site.register(RPService, BaseServiceAdmin)
admin.site.register(AccountService, ServiceWithImagesAdmin)
admin.site.register(DonationService, ServiceWithImagesAdmin)
admin.site.register(BoostService, BaseServiceAdmin)
admin.site.register(TrainingService, BaseServiceAdmin)
admin.site.register(BattlePassService, BaseServiceAdmin)
admin.site.register(OtherService, BaseServiceAdmin)
admin.site.register(QualificationService, BaseServiceAdmin)
admin.site.register(GeneralService, BaseServiceAdmin)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
