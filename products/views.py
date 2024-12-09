import logging

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import TemplateView

from .models import Category


# Create your views here.


class ProductsView(TemplateView):
    template_name = "products/products.html"
    title = "Услуги"

    def get_context_data(self, **kwargs):
        # Получаем все категории
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get("category_slug")  # Передаем slug категории в URL

        # Если категория выбрана, получаем ее объект, иначе берем первую категорию
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
        else:
            category = Category.objects.first()  # Если slug не указан, берем первую категорию по умолчанию

        context["categories"] = Category.objects.all()  # Добавляем все категории в контекст
        context["category"] = category  # Передаем выбранную категорию
        return context


class CategoryDescriptionView(View):
    def get(self, request, category_slug):
        logging.info(f"Получен запрос на категорию с slug: {category_slug}")

        category = get_object_or_404(Category, slug=category_slug)

        logging.info(f"Описание категории: {category.description}")

        return JsonResponse({"description": category.description})
