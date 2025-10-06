from django.contrib import admin

from .models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    """Отображение новостей в административной панели."""
    list_display = ('title', 'published_at', 'created_at', 'updated_at')
    list_filter = ('published_at',)
    search_fields = ('title', 'description')
    ordering = ('-published_at',)
