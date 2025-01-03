import logging
from itertools import product
from pyexpat import model
from venv import logger

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views import View
from django.views.generic import ListView, TemplateView

from .mixins import CategoryMixin, SearchDescriptionMixin, ServerMixin
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
    TrainingService,
)


# Create your views here.
logger = logging.getLogger(__name__)


class CategoryView(View):
    model = Category
    title = "Услуги"
    template_name = "products/products.html"
    context_object_name = "categories"


class AccountServiceListView(CategoryMixin, SearchDescriptionMixin, ServerMixin, ListView):
    """
    Вьюха для отображения списка услуг категории "Account".
    """

    model = AccountService
    template_name = "products/account.html"  # Указываем путь к твоему шаблону
    context_object_name = "services"  # Имя переменной для доступа к данным в шаблоне
    paginate_by = 10  # Если нужна пагинация, можно задать количество записей на страницу

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        kwargs["slug"] = "accounts"  # или динамически передавайте нужный слаг
        context = super().get_context_data(**kwargs)
        context["filter_options"] = [{"value": key, "label": label} for key, label in AccountService.FILTER_CHOICES]
        context["ranks"] = AccountService.RANK_CHOICES
        return context


class RPServiceListView(CategoryMixin, ServerMixin, ListView):
    """
    Вьюха для отображения списка услуг категории "Account".
    """

    model = RPService
    template_name = "products/riot-points.html"  # Указываем путь к твоему шаблону
    context_object_name = "services"  # Имя переменной для доступа к данным в шаблоне
    paginate_by = 10  # Если нужна пагинация, можно задать количество записей на страницу

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        kwargs["slug"] = "riot-points"  # или динамически передавайте нужный слаг

        context = super().get_context_data(**kwargs)
        context["filter_options"] = [{"value": key, "label": label} for key, label in RPService.FILTER_CHOICES]
        return context


class BoostServiceListView(CategoryMixin, SearchDescriptionMixin, ServerMixin, ListView):
    """
    Вьюха для отображения списка услуг категории "Account".
    """

    model = BoostService
    template_name = "products/boost.html"  # Указываем путь к твоему шаблону
    context_object_name = "services"  # Имя переменной для доступа к данным в шаблоне
    paginate_by = 10  # Если нужна пагинация, можно задать количество записей на страницу

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        kwargs["slug"] = "boosting"  # или динамически передавайте нужный слаг

        context = super().get_context_data(**kwargs)
        context["filter_options"] = BoostService.FILTER_CHOICES
        context["ranges"] = BoostService.RANK_RANGE_CHOICES
        return context


class TrainingServiceListView(CategoryMixin, SearchDescriptionMixin, ListView):
    """
    Вьюха для отображения списка услуг категории "Account".
    """

    model = TrainingService
    template_name = "products/training.html"  # Указываем путь к твоему шаблону
    context_object_name = "services"  # Имя переменной для доступа к данным в шаблоне
    paginate_by = 10  # Если нужна пагинация, можно задать количество записей на страницу

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        kwargs["slug"] = "training"  # или динамически передавайте нужный слаг

        context = super().get_context_data(**kwargs)
        context["positions"] = TrainingService.FILTER_CHOICES
        return context


class BattlePassServiceListView(CategoryMixin, SearchDescriptionMixin, ListView):
    """
    Вьюха для отображения списка услуг категории "Account".
    """

    model = BattlePassService
    template_name = "products/battlepass.html"  # Указываем путь к твоему шаблону
    context_object_name = "services"  # Имя переменной для доступа к данным в шаблоне
    paginate_by = 10  # Если нужна пагинация, можно задать количество записей на страницу

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        kwargs["slug"] = "battle-pass"  # или динамически передавайте нужный слаг

        context = super().get_context_data(**kwargs)
        context["filter_options"] = [{"value": key, "label": label} for key, label in BattlePassService.FILTER_CHOICES]
        return context


class DonationServiceListView(CategoryMixin, SearchDescriptionMixin, ServerMixin, ListView):
    """
    Вьюха для отображения списка услуг категории "Account".
    """

    model = DonationService
    template_name = "products/donation.html"  # Указываем путь к твоему шаблону
    context_object_name = "services"  # Имя переменной для доступа к данным в шаблоне
    paginate_by = 10  # Если нужна пагинация, можно задать количество записей на страницу

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        kwargs["slug"] = "donation"  # или динамически передавайте нужный слаг

        context = super().get_context_data(**kwargs)
        context["filter_options"] = [{"value": key, "label": label} for key, label in DonationService.FILTER_CHOICES]
        context["ways"] = DonationService.RECEIVING_METHOD_CHOICES
        return context


class GeneralServiceListView(CategoryMixin, SearchDescriptionMixin, ListView):
    """
    Вьюха для отображения списка услуг категории "Account".
    """

    model = GeneralService
    template_name = "products/services.html"  # Указываем путь к твоему шаблону
    context_object_name = "services"  # Имя переменной для доступа к данным в шаблоне
    paginate_by = 10  # Если нужна пагинация, можно задать количество записей на страницу

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        kwargs["slug"] = "services"  # или динамически передавайте нужный слаг

        context = super().get_context_data(**kwargs)
        context["filter_options"] = GeneralService.FILTER_CHOICES
        return context


class OtherServiceListView(CategoryMixin, SearchDescriptionMixin, ListView):
    """
    Вьюха для отображения списка услуг категории "Account".
    """

    model = OtherService
    template_name = "products/other.html"  # Указываем путь к твоему шаблону
    context_object_name = "services"  # Имя переменной для доступа к данным в шаблоне
    paginate_by = 10  # Если нужна пагинация, можно задать количество записей на страницу

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        kwargs["slug"] = "other"  # или динамически передавайте нужный слаг

        context = super().get_context_data(**kwargs)
        context["filter_options"] = OtherService.FILTER_CHOICES
        return context


class QualificationServiceListView(CategoryMixin, SearchDescriptionMixin, ListView):
    """
    Вьюха для отображения списка услуг категории "Account".
    """

    model = QualificationService
    template_name = "products/qualification.html"  # Указываем путь к твоему шаблону
    context_object_name = "services"  # Имя переменной для доступа к данным в шаблоне
    paginate_by = 10  # Если нужна пагинация, можно задать количество записей на страницу

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        kwargs["slug"] = "qualification"  # или динамически передавайте нужный слаг
        context = super().get_context_data(**kwargs)
        return context


# class ProductsView(TemplateView):
#     template_name = "products/products.html"
#     title = "Услуги"

#     def get_context_data(self, **kwargs):
#         # Получаем все категории
#         context = super().get_context_data(**kwargs)
#         category_slug = self.kwargs.get("category_slug")  # Передаем slug категории в URL

#         # Если slug не передан, перенаправляем на первую категорию
#         if category_slug:
#             category = get_object_or_404(Category, slug=category_slug)
#         else:
#             category = Category.objects.first()  # Выбираем первую категорию по умолчанию

#         # Если категория указана, берем ее
#         context["category"] = category  # Передаем выбранную категорию
#         context["categories"] = Category.objects.all()  # Добавляем все категории в контекст
#         context["servers"] = ServerBasedService.SERVER_CHOICES
#         context["filter_options_rp"] = [{"value": key, "label": label} for key, label in RPService.FILTER_CHOICES]
#         context["filter_options_accounts"] = [
#             {"value": key, "label": label} for key, label in AccountService.FILTER_CHOICES
#         ]
#         return context

#     def get_category_content(request, category_slug):
#         category = get_object_or_404(Category, slug=category_slug)

#         # Рендерим нужный шаблон в зависимости от категории
#         if category.slug == "riot-points":
#             content = render_to_string("products/riot-points.html", {"category": category})
#         elif category.slug == "another-category":
#             content = render_to_string("products/another-category.html", {"category": category})
#         else:
#             content = "<p>Контент для этой категории еще не доступен.</p>"

#         return JsonResponse({"content": content})


# class AccountView(ProductsView):
#     template_name = "products/account.html"
#     title = "Покупка аккаунта"


# class CategoryDescriptionView(View):
#     def get(self, request, category_slug):
#         logging.info(f"Получен запрос на категорию с slug: {category_slug}")

#         category = get_object_or_404(Category, slug=category_slug)

#         logging.info(f"Описание категории: {category.description}")

#         # Просто возвращаем описание категории как JSON
#         return JsonResponse({"description": category.description})


# class BaseServiceView(View):
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["servers"] = ServerBasedService.SERVER_CHOICES  # Добавляем серверы в общий контекст
#         return context

#     def get(self, request, *args, **kwargs):
#         context = self.get_context_data(**kwargs)  # Получаем контекст
#         return render(request, "products.html", context)
