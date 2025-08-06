from django.contrib import admin

from .models import Order, Review


'Теперь можно зайти в админку и увидеть заказы.'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'seller', 'description', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'product__title')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'seller', 'rating', 'order', 'created_at')
    search_fields = ('author__username', 'seller__username', 'comment')
    list_filter = ('rating', 'created_at')
