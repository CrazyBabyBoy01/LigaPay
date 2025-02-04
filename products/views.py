import logging
from itertools import product
from pyexpat import model
from urllib import request
from venv import logger

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views import View
from django.views.generic import FormView, ListView, TemplateView

from products.filters import AccountFilter, BoostFilter, RpFilter
from products.forms import (
    AccountServiceFilterForm,
    AccountServiceForm,
    BoostServiceFilterForm,
    BoostServiceForm,
    RPServiceFilterForm,
    RPServiceForm,
)

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

    def get(self, request, slug=None):
        if slug:
            # Если слаг передан, получаем соответствующую категорию
            category = get_object_or_404(Category, slug=slug)
            return render(
                request,
                self.template_name,
                {
                    "categories": category,
                    "title": self.title,
                },
            )


class AccountServiceListView(CategoryMixin, SearchDescriptionMixin, ServerMixin, ListView):
    """
    Вьюха для отображения списка услуг категории "Account".
    """

    title = "Аккаунты"
    model = AccountService
    template_name = "products/account.html"  # Указываем путь к твоему шаблону
    context_object_name = "services"  # Имя переменной для доступа к данным в шаблоне
    paginate_by = 10  # Если нужна пагинация, можно задать количество записей на страницу

    def get_queryset(self):
        queryset = self.model.objects.all()
        filter_form = AccountServiceFilterForm(self.request.GET)
        if filter_form.is_valid():
            queryset = AccountFilter(self.request.GET, queryset=queryset, request=self.request).qs
        return queryset

    def get_context_data(self, **kwargs):  # для передачи контекста в шаблон
        kwargs["slug"] = "accounts"  # для отображения на странице заголовка и опсиания для категории (динамически)
        context = super().get_context_data(**kwargs)
        context["filter_form"] = AccountServiceFilterForm(self.request.GET)
        context["form"] = AccountServiceForm()
        return context

    def post(self, request, *args, **kwargs):
        form = AccountServiceForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)  # Не сохраняем сразу, а создаем объект
            offer.seller = request.user  # Привязываем авторизованного пользователя как продавца
            form.save()  # Сохраняем данные формы
            return redirect("products:account")  # Здесь можно перенаправить на страницу успеха

        # Добавление ошибок в лог или отладочную информацию
        # Логируем ошибки
        logger.error(f"Ошибка в форме: {form.errors}")
        return self.get(request, *args, **kwargs)  # Возвращаем форму с ошибками
        # Если форма не валидна, возвращаем ее с ошибками
        return self.get(request, *args, **kwargs)  # В данном случае, снова вызываем get и передаем форму с ошибками


class RPServiceListView(CategoryMixin, ListView):
    """
    Вьюха для отображения списка услуг категории "Account".
    """

    model = RPService
    template_name = "products/riot-points.html"  # Указываем путь к твоему шаблону
    context_object_name = "services"  # Имя переменной для доступа к данным в шаблоне
    paginate_by = 10  # Если нужна пагинация, можно задать количество записей на страницу

    def get_queryset(self):
        queryset = self.model.objects.all()
        filter_form = RPServiceFilterForm(self.request.GET)
        if filter_form.is_valid():
            queryset = RpFilter(self.request.GET, queryset=queryset, request=self.request).qs
        return queryset

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        kwargs["slug"] = "riot-points"  # или динамически передавайте нужный слаг

        context = super().get_context_data(**kwargs)
        context["filter_form"] = RPServiceFilterForm(self.request.GET)
        context["form"] = RPServiceForm()
        return context

    def post(self, request, *args, **kwargs):
        form = RPServiceForm(request.POST)
        print("ldjlsajdlsajl")
        if form.is_valid():
            offer = form.save(commit=False)  # Не сохраняем сразу, а создаем объект
            offer.seller = request.user  # Привязываем авторизованного пользователя как продавца
            form.save()  # Сохраняем данные формы
            return redirect("products:riot-points")  # Здесь можно перенаправить на страницу успеха


class BoostServiceListView(CategoryMixin, SearchDescriptionMixin, ServerMixin, ListView):
    """
    Вьюха для отображения списка услуг категории "Boost".
    """

    model = BoostService
    template_name = "products/boost.html"  # Указываем путь к твоему шаблону
    context_object_name = "services"  # Имя переменной для доступа к данным в шаблоне
    paginate_by = 10  # Если нужна пагинация, можно задать количество записей на страницу

    def get_queryset(self):
        queryset = self.model.objects.all()
        filter_form = BoostServiceFilterForm(self.request.GET)
        if filter_form.is_valid():
            queryset = BoostFilter(self.request.GET, queryset=queryset, request=self.request).qs
        return queryset

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        kwargs["slug"] = "boosting"  # или динамически передавайте нужный слаг

        context = super().get_context_data(**kwargs)
        context["filter_form"] = BoostServiceFilterForm(self.request.GET)
        context["form"] = BoostServiceForm()
        return context

    def post(self, request, *args, **kwargs):
        form = BoostServiceForm(request.POST)
        print("ldjlsajdlsajl")
        if form.is_valid():
            offer = form.save(commit=False)  # Не сохраняем сразу, а создаем объект
            offer.seller = request.user  # Привязываем авторизованного пользователя как продавца
            form.save()  # Сохраняем данные формы
            return redirect("products:boost")  # Здесь можно перенаправить на страницу успеха


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


# class OfferView(TemplateView):
#     template_name = "products/offer.html"
#     context_object_name = "offers"

#     def get(self, request, *args, **kwargs):
#         # Получаем выбранную категорию из URL или из запроса
#         category_slug = self.kwargs.get("slug", None)  # Или используй kwargs, если передаешь через URL

#         # Создаем форму
#         form = GeneralOfferForm()

#         # Динамически скрываем или показываем поля в зависимости от категории
#         if category_slug == "accounts":
#             form.fields["rank"].required = True
#             form.fields["server"].required = True
#             form.fields["position"].required = False
#         return render(request, self.template_name, {"form": form, "category_slug": category_slug})
#     def post(self, request, *args, **kwargs):
#         category_slug = self.kwargs.get("slug")
#         category = get_object_or_404(Category, slug=category_slug)
#         form = GeneralOfferForm(request.POST, category=category)

#         if form.is_valid():
#             offer = form.save(commit=False)
#             offer.category = category  # Привязываем категорию
#             offer.save()
#             return redirect("products:account")  # Укажите URL успеха
#         return render(request, self.template_name, {"form": form, "category": category})
