import logging
from itertools import product
from pyexpat import model
from urllib import request
from venv import logger

from chat.mixin import GroupedMessagesMixin
from chat.models import ChatMessage
from common.views import ContextMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, FormView, ListView, TemplateView
from orders.models import Order, Review

from products.filters import (
    AccountFilter,
    BattlePassFilter,
    BoostFilter,
    DonationFilter,
    GeneralFilter,
    OtherFilter,
    QualificationFilter,
    RpFilter,
    TrainingFilter,
)
from products.forms import (
    AccountServiceFilterForm,
    AccountServiceForm,
    BattlePassServiceFilterForm,
    BattlePassServiceForm,
    BoostServiceFilterForm,
    BoostServiceForm,
    DonationServiceFilterForm,
    DonationServiceForm,
    GeneralServiceFilterForm,
    GeneralServiceForm,
    OtherServiceFilterForm,
    OtherServiceForm,
    PurchaseForm,
    QualificationServiceFilterForm,
    QualificationServiceForm,
    RPServiceFilterForm,
    RPServiceForm,
    ServiceImageForm,
    TrainingServiceFilterForm,
    TrainingServiceForm,
)

from .mixins import (
    CategoryMixin,
    ChatMixin,
    ExcludeOwnServicesMixin,  # Этот миксин должен быть первым!
    PaginateMixin,
    SearchDescriptionMixin,
    ServiceChatMixin,
)
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


class AccountServiceListView(CategoryMixin, ChatMixin, SearchDescriptionMixin, ContextMixin, PaginateMixin, ListView):
    """
    Вьюха для отображения списка услуг категории "Account".
    """

    title = "Аккаунты"
    model = AccountService
    template_name = "products/account.html"  # Указываем путь к твоему шаблону
    context_object_name = "services"  # Имя переменной для доступа к данным в шаблоне

    def get_queryset(self):
        print("🔍 Запрашиваем queryset для AccountServiceListView")
        # queryset = self.model.objects.all().order_by("id")

        # Получаем все услуги (карточки) для текущего пользователя
        queryset = self.model.objects.all().order_by("id")

        user = self.request.user
        if user.is_authenticated:
            # Преобразуем ленивый объект в обычный
            user = user._wrapped if hasattr(user, "_wrapped") else user  # noqa: SLF001
            print(f"🔐 Пользователь авторизован — исключаем его карточки: {user}")
            queryset = queryset.exclude(seller=user)
        else:
            print("🕵️ Пользователь анонимный — показываем все услуги")

        filter_form = AccountServiceFilterForm(self.request.GET)
        if filter_form.is_valid():
            queryset = AccountFilter(filter_form.cleaned_data, queryset=queryset, request=self.request).qs
        return queryset

    def get_context_data(self, **kwargs):  # для передачи контекста в шаблон
        kwargs["slug"] = "accounts"  # для отображения на странице заголовка и опсиания для категории (динамически)
        context = super().get_context_data(**kwargs)
        context["filter_form"] = AccountServiceFilterForm(self.request.GET)
        context["form"] = AccountServiceForm()
        context["image_form"] = ServiceImageForm()  # Добавляем форму для загрузки картинки
        return context

    def post(self, request, *args, **kwargs):
        form = AccountServiceForm(request.POST)
        image_form = ServiceImageForm(request.POST, request.FILES)  # Форма для картинки с файлами
        if form.is_valid():
            offer = form.save(commit=False)  # Не сохраняем сразу, а создаем объект
            offer.seller = request.user  # Привязываем авторизованного пользователя как продавца
            form.save()  # Сохраняем данные формы
            # Обработка загруженных файлов (картинок)
            if image_form.is_valid() and image_form.cleaned_data.get("image"):
                image = image_form.save(commit=False)
                image.content_object = offer  # Связываем картинку с сервисом
                image.save()

            return redirect("products:account")  # Здесь можно перенаправить на страницу успеха

        # Добавление ошибок в лог или отладочную информацию
        # Логируем ошибки
        logger.error(f"Ошибка в форме: {form.errors}")
        return self.get(request, *args, **kwargs)  # Возвращаем форму с ошибками
        # Если форма не валидна, возвращаем ее с ошибками
        return self.get(request, *args, **kwargs)  # В данном случае, снова вызываем get и передаем форму с ошибками


class AccountServiceDetailView(CategoryMixin, ServiceChatMixin, GroupedMessagesMixin, ContextMixin, DetailView):
    title = "Покупка Аккунта"
    model = AccountService
    template_name = "products/account_detail.html"  # Путь к шаблону
    form_class = AccountServiceForm
    context_object_name = "service"

    def get_object(self):
        """Получает объект AccountService по ID или возвращает 404."""
        return get_object_or_404(AccountService, id=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        self.object = self.get_object()
        kwargs["slug"] = "accounts"  # или динамически передавайте нужный слаг

        context = super().get_context_data(**kwargs)
        service = self.get_object()
        context["form"] = AccountServiceForm(instance=service)
        context["form_purchase"] = PurchaseForm()  # форма для покупки
        context["is_buyer"] = self.request.user != self.object.seller  # Проверка, покупатель ли это
        context["model_name"] = self.model._meta.model_name
        context["image_form"] = ServiceImageForm()  # Добавляем картинку
        context["images"] = self.object.images.all()
        context["seller_reviews"] = Review.objects.filter(seller=service.seller).order_by("-id")
        # Только для авторизованных пользователей — проверка заказов
        if self.request.user.is_authenticated:
            pending_order = Order.objects.filter(
                content_type=ContentType.objects.get_for_model(service),
                object_id=service.id,
                user=self.request.user,
                status="pending",
            ).first()
        else:
            pending_order = None

        context["pending_order"] = pending_order
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        service = self.get_object()

        # Проверка, что пользователь — продавец
        if service.seller != request.user:
            return JsonResponse({"success": False, "message": "У вас нет прав на это действие."})
        # Удаление изображения
        if "delete_image" in request.POST:
            image_id = request.POST.get("image_id")
            image = get_object_or_404(service.images, id=image_id)
            image.delete()
            return JsonResponse({"success": True, "message": "Изображение удалено."})

        # Добавление нового изображения
        if "add_image" in request.POST:
            if service.images.count() >= 4:
                return JsonResponse({"success": False, "message": "Максимум 4 изображения разрешено."})

            image_form = ServiceImageForm(request.POST, request.FILES)
            if image_form.is_valid():
                new_img = image_form.save(commit=False)
                new_img.content_object = service
                new_img.save()
                return JsonResponse({"success": True, "message": "Изображение добавлено."})
            return JsonResponse(
                {"success": False, "message": "Ошибка при загрузке изображения.", "errors": image_form.errors.as_json()}
            )

        # Удаление
        if "delete" in request.POST:
            service.delete()
            return redirect("products:my_products")

        # Редактирование
        form = AccountServiceForm(request.POST, instance=service)
        image_form = ServiceImageForm(request.POST, request.FILES)

        if form.is_valid():
            offer = form.save()

            # Если загрузили картинку — сохраняем её
            if image_form.is_valid() and image_form.cleaned_data.get("image"):
                new_img = image_form.save(commit=False)
                new_img.content_object = offer
                new_img.save()
            return redirect("products:accounts_detail", pk=service.pk)

        # Если форма невалидна, отрисуем снова с ошибками
        context = self.get_context_data(object=service)
        context["form"] = form
        context["image_form"] = image_form
        return self.render_to_response(context)


class RPServiceListView(ExcludeOwnServicesMixin, CategoryMixin, ChatMixin, PaginateMixin, ContextMixin, ListView):
    model = RPService
    template_name = "products/riot-points.html"  # Указываем путь к твоему шаблону
    context_object_name = "services"  # Имя переменной для доступа к данным в шаблоне
    title = "RP"

    def get_queryset(self):
        print("🔍 Запрашиваем queryset для RPServiceListView")
        # queryset = self.model.objects.all().order_by("id")

        # Получаем все услуги (карточки) для текущего пользователя и не равно 0
        queryset = self.model.objects.filter(quantity__gt=0).order_by("id")

        user = self.request.user
        if user.is_authenticated:
            # Преобразуем ленивый объект в обычный
            user = user._wrapped if hasattr(user, "_wrapped") else user  # noqa: SLF001
            print(f"🔐 Пользователь авторизован — исключаем его карточки: {user}")
            queryset = queryset.exclude(seller=user)
        else:
            print("🕵️ Пользователь анонимный — показываем все услуги")

        filter_form = RPServiceFilterForm(self.request.GET)
        if filter_form.is_valid():
            queryset = RpFilter(filter_form.cleaned_data, queryset=queryset, request=self.request).qs
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
        if form.is_valid():
            offer = form.save(commit=False)  # Не сохраняем сразу, а создаем объект
            offer.seller = request.user  # Привязываем авторизованного пользователя как продавца
            form.save()  # Сохраняем данные формы
            return redirect("products:riot-points")  # Здесь можно перенаправить на страницу успеха


class RPServiceDetailView(CategoryMixin, ServiceChatMixin, GroupedMessagesMixin, ContextMixin, DetailView):
    """Представление для отображения деталей услуги (RPService)."""

    title = "Покупка RP"
    model = RPService
    template_name = "products/riot-points_detail.html"  # Путь к шаблону
    form_class = RPServiceForm
    context_object_name = "service"

    def get_object(self):
        """Получает объект RPService по ID или возвращает 404."""
        return get_object_or_404(RPService, id=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        kwargs["slug"] = "riot-points"  # или динамически передавайте нужный слаг

        context = super().get_context_data(**kwargs)
        service = self.get_object()
        context["form"] = RPServiceForm(instance=service)
        context["form_purchase"] = PurchaseForm()  # форма для покупки
        context["is_buyer"] = self.request.user != self.object.seller  # Проверка, покупатель ли это
        context["model_name"] = self.model._meta.model_name
        context["seller_reviews"] = Review.objects.filter(seller=service.seller).order_by("-id")
        # Только для авторизованных пользователей — проверка заказов
        if self.request.user.is_authenticated:
            pending_order = Order.objects.filter(
                content_type=ContentType.objects.get_for_model(service),
                object_id=service.id,
                user=self.request.user,
                status="pending",
            ).first()
        else:
            pending_order = None

        context["pending_order"] = pending_order
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        service = self.get_object()

        # Проверка, что пользователь — продавец
        if service.seller != request.user:
            return HttpResponseForbidden("У вас нет прав на это действие.")

        # Удаление
        if "delete" in request.POST:
            service.delete()
            return redirect("products:my_products")

        # Редактирование
        form = RPServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect("products:riot-points_detail", pk=service.pk)

        # Если форма невалидна, отрисуем снова с ошибками
        context = self.get_context_data(object=service)
        context["form"] = form
        return self.render_to_response(context)


class BoostServiceListView(CategoryMixin, ChatMixin, SearchDescriptionMixin, ContextMixin, PaginateMixin, ListView):
    """
    Вьюха для отображения списка услуг категории "Boost".
    """

    title = "Буст"
    model = BoostService
    template_name = "products/boost.html"  # Указываем путь к твоему шаблону
    context_object_name = "services"  # Имя переменной для доступа к данным в шаблоне

    def get_queryset(self):
        print("🔍 Запрашиваем queryset для RPServiceListView")
        # queryset = self.model.objects.all().order_by("id")

        # Получаем все услуги (карточки) для текущего пользователя
        queryset = self.model.objects.all().order_by("id")

        user = self.request.user
        if user.is_authenticated:
            # Преобразуем ленивый объект в обычный
            print(f"🔐 Пользователь авторизован — исключаем его карточки: {user}")
            queryset = queryset.exclude(seller=user)
        else:
            print("🕵️ Пользователь анонимный — показываем все услуги")
        filter_form = BoostServiceFilterForm(self.request.GET)
        if filter_form.is_valid():
            queryset = BoostFilter(filter_form.cleaned_data, queryset=queryset, request=self.request).qs
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
        if form.is_valid():
            offer = form.save(commit=False)  # Не сохраняем сразу, а создаем объект
            offer.seller = request.user  # Привязываем авторизованного пользователя как продавца
            form.save()  # Сохраняем данные формы
            return redirect("products:boost")  # Здесь можно перенаправить на страницу успеха


class BoostServiceDetailsView(CategoryMixin, ServiceChatMixin, GroupedMessagesMixin, ContextMixin, DetailView):
    """Представление для отображения деталей услуги (RPService)."""

    title = "Буст аккаунта"
    model = BoostService
    template_name = "products/boost_detail.html"  # Путь к шаблону
    form_class = BoostServiceForm
    context_object_name = "service"

    def get_object(self):
        """Получает объект RPService по ID или возвращает 404."""
        return get_object_or_404(BoostService, id=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        kwargs["slug"] = "boosting"  # или динамически передавайте нужный слаг

        context = super().get_context_data(**kwargs)
        service = self.get_object()
        context["form"] = BoostServiceForm(instance=service)
        context["form_purchase"] = PurchaseForm()  # форма для покупки
        context["is_buyer"] = self.request.user != self.object.seller  # Проверка, покупатель ли это
        context["model_name"] = self.model._meta.model_name
        context["seller_reviews"] = Review.objects.filter(seller=service.seller).order_by("-id")
        #  Получаем заказ с этим товаром и статусом "pending"
        # Только для авторизованных пользователей — проверка заказов
        if self.request.user.is_authenticated:
            pending_order = Order.objects.filter(
                content_type=ContentType.objects.get_for_model(service),
                object_id=service.id,
                user=self.request.user,
                status="pending",
            ).first()
        else:
            pending_order = None

        context["pending_order"] = pending_order
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        service = self.get_object()

        # Проверка, что пользователь — продавец
        if service.seller != request.user:
            return HttpResponseForbidden("У вас нет прав на это действие.")

        # Удаление
        if "delete" in request.POST:
            service.delete()
            return redirect("products:my_products")

        # Редактирование
        form = BoostServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect("products:boost_detail", pk=service.pk)

        # Если форма невалидна, отрисуем снова с ошибками
        context = self.get_context_data(object=service)
        context["form"] = form
        return self.render_to_response(context)


class TrainingServiceListView(CategoryMixin, ChatMixin, SearchDescriptionMixin, ContextMixin, PaginateMixin, ListView):
    """
    Вьюха для отображения списка услуг категории "Account".
    """

    title = "Обучение"
    model = TrainingService
    template_name = "products/training.html"  # Указываем путь к твоему шаблону
    context_object_name = "services"  # Имя переменной для доступа к данным в шаблоне

    def get_queryset(self):
        queryset = self.model.objects.all().order_by("id")
        user = self.request.user
        if user.is_authenticated:
            # Преобразуем ленивый объект в обычный
            print(f"🔐 Пользователь авторизован — исключаем его карточки: {user}")
            queryset = queryset.exclude(seller=user)
        else:
            print("🕵️ Пользователь анонимный — показываем все услуги")
        filter_form = TrainingServiceFilterForm(self.request.GET)
        if filter_form.is_valid():
            queryset = TrainingFilter(filter_form.cleaned_data, queryset=queryset, request=self.request).qs
        return queryset

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        kwargs["slug"] = "training"  # или динамически передавайте нужный слаг

        context = super().get_context_data(**kwargs)
        context["filter_form"] = TrainingServiceFilterForm(self.request.GET)
        context["form"] = TrainingServiceForm()
        return context

    def post(self, request, *args, **kwargs):
        form = TrainingServiceForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)  # Не сохраняем сразу, а создаем объект
            offer.seller = request.user  # Привязываем авторизованного пользователя как продавца
            form.save()  # Сохраняем данные формы
            return redirect("products:training")  # Здесь можно перенаправить на страницу успеха


class TrainingServiceDetailsView(CategoryMixin, ServiceChatMixin, GroupedMessagesMixin, ContextMixin, DetailView):
    """Представление для отображения деталей услуги (TrainingService)."""

    title = "Обучение"
    model = TrainingService
    template_name = "products/training_detail.html"  # Путь к шаблону
    form_class = TrainingServiceForm
    context_object_name = "service"

    def get_object(self):
        """Получает объект RPService по ID или возвращает 404."""
        return get_object_or_404(TrainingService, id=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        kwargs["slug"] = "training"  # или динамически передавайте нужный слаг

        context = super().get_context_data(**kwargs)
        service = self.get_object()
        context["form"] = TrainingServiceForm(instance=service)
        context["form_purchase"] = PurchaseForm()  # форма для покупки
        context["is_buyer"] = self.request.user != self.object.seller  # Проверка, покупатель ли это
        context["model_name"] = self.model._meta.model_name
        context["seller_reviews"] = Review.objects.filter(seller=service.seller).order_by("-id")
        #  Получаем заказ с этим товаром и статусом "pending"
        # Только для авторизованных пользователей — проверка заказов
        if self.request.user.is_authenticated:
            pending_order = Order.objects.filter(
                content_type=ContentType.objects.get_for_model(service),
                object_id=service.id,
                user=self.request.user,
                status="pending",
            ).first()
        else:
            pending_order = None

        context["pending_order"] = pending_order
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        service = self.get_object()

        # Проверка, что пользователь — продавец
        if service.seller != request.user:
            return HttpResponseForbidden("У вас нет прав на это действие.")

        # Удаление
        if "delete" in request.POST:
            service.delete()
            return redirect("products:my_products")

        # Редактирование
        form = TrainingServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect("products:training_detail", pk=service.pk)

        # Если форма невалидна, отрисуем снова с ошибками
        context = self.get_context_data(object=service)
        context["form"] = form
        return self.render_to_response(context)


class BattlePassServiceListView(
    CategoryMixin, ChatMixin, SearchDescriptionMixin, ContextMixin, PaginateMixin, ListView
):
    """
    Вьюха для отображения списка услуг категории "BattlePass".
    """

    title = "Боевой пропуск"
    model = BattlePassService
    template_name = "products/battlepass.html"  # Указываем путь к твоему шаблону
    context_object_name = "services"  # Имя переменной для доступа к данным в шаблоне

    def get_queryset(self):
        queryset = self.model.objects.all().order_by("id")
        user = self.request.user
        if user.is_authenticated:
            # Преобразуем ленивый объект в обычный
            print(f"🔐 Пользователь авторизован — исключаем его карточки: {user}")
            queryset = queryset.exclude(seller=user)
        else:
            print("🕵️ Пользователь анонимный — показываем все услуги")
        filter_form = BattlePassServiceFilterForm(self.request.GET)
        if filter_form.is_valid():
            queryset = BattlePassFilter(filter_form.cleaned_data, queryset=queryset, request=self.request).qs
        return queryset

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        kwargs["slug"] = "battle-pass"  # или динамически передавайте нужный слаг

        context = super().get_context_data(**kwargs)
        context["filter_form"] = BattlePassServiceFilterForm(self.request.GET)
        context["form"] = BattlePassServiceForm()
        return context

    def post(self, request, *args, **kwargs):
        form = BattlePassServiceForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)  # Не сохраняем сразу, а создаем объект
            offer.seller = request.user  # Привязываем авторизованного пользователя как продавца
            form.save()  # Сохраняем данные формы
            return redirect("products:battlepass")  # Здесь можно перенаправить на страницу успеха


class BattlePassServiceDetailsView(CategoryMixin, ServiceChatMixin, GroupedMessagesMixin, ContextMixin, DetailView):
    """Представление для отображения деталей услуги (BattlePassService)."""

    title = "Обучение"
    model = BattlePassService
    template_name = "products/battlepass_detail.html"  # Путь к шаблону
    form_class = BattlePassServiceForm
    context_object_name = "service"

    def get_object(self):
        """Получает объект BattlePassService по ID или возвращает 404."""
        return get_object_or_404(BattlePassService, id=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        kwargs["slug"] = "battle-pass"  # или динамически передавайте нужный слаг

        context = super().get_context_data(**kwargs)
        service = self.get_object()
        context["form"] = BattlePassServiceForm(instance=service)
        context["form_purchase"] = PurchaseForm()  # форма для покупки
        context["is_buyer"] = self.request.user != self.object.seller  # Проверка, покупатель ли это
        context["model_name"] = self.model._meta.model_name
        context["seller_reviews"] = Review.objects.filter(seller=service.seller).order_by("-id")
        #  Получаем заказ с этим товаром и статусом "pending"
        # Только для авторизованных пользователей — проверка заказов
        if self.request.user.is_authenticated:
            pending_order = Order.objects.filter(
                content_type=ContentType.objects.get_for_model(service),
                object_id=service.id,
                user=self.request.user,
                status="pending",
            ).first()
        else:
            pending_order = None

        context["pending_order"] = pending_order
        return context

    def post(self, request, *args, **kwargs):
        service = self.get_object()

        # Проверка, что пользователь — продавец
        if service.seller != request.user:
            return HttpResponseForbidden("У вас нет прав на это действие.")

        # Удаление
        if "delete" in request.POST:
            service.delete()
            return redirect("products:my_products")

        # Редактирование
        form = BattlePassServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect("products:battlepass_detail", pk=service.pk)

        # Если форма невалидна, отрисуем снова с ошибками
        context = self.get_context_data(object=service)
        context["form"] = form
        return self.render_to_response(context)


class DonationServiceListView(CategoryMixin, ChatMixin, SearchDescriptionMixin, ContextMixin, PaginateMixin, ListView):
    """
    Вьюха для отображения списка услуг категории "Account".
    """

    title = "Донат"
    model = DonationService
    template_name = "products/donation.html"  # Указываем путь к твоему шаблону
    context_object_name = "services"  # Имя переменной для доступа к данным в шаблоне

    def get_queryset(self):
        queryset = self.model.objects.all().order_by("id")
        user = self.request.user
        if user.is_authenticated:
            # Преобразуем ленивый объект в обычный
            print(f"🔐 Пользователь авторизован — исключаем его карточки: {user}")
            queryset = queryset.exclude(seller=user)
        else:
            print("🕵️ Пользователь анонимный — показываем все услуги")
        filter_form = DonationServiceFilterForm(self.request.GET)
        if filter_form.is_valid():
            queryset = DonationFilter(filter_form.cleaned_data, queryset=queryset, request=self.request).qs
        return queryset

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        kwargs["slug"] = "donation"  # или динамически передавайте нужный слаг

        context = super().get_context_data(**kwargs)
        context["filter_form"] = DonationServiceFilterForm(self.request.GET)
        context["form"] = DonationServiceForm()
        context["image_form"] = ServiceImageForm()  # Добавляем форму для загрузки картинки
        return context

    def post(self, request, *args, **kwargs):
        form = DonationServiceForm(request.POST)
        image_form = ServiceImageForm(request.POST, request.FILES)  # Форма для картинки с файлами
        if form.is_valid():
            offer = form.save(commit=False)  # Не сохраняем сразу, а создаем объект
            offer.seller = request.user  # Привязываем авторизованного пользователя как продавца
            form.save()  # Сохраняем данные формы
            # Обработка загруженных файлов (картинок)
            if image_form.is_valid() and image_form.cleaned_data.get("image"):
                image = image_form.save(commit=False)
                image.content_object = offer  # Связываем картинку с сервисом
                image.save()
            return redirect("products:donation")  # Здесь можно перенаправить на страницу успеха
        return redirect("products:donation")


class DonationServiceDetailsView(CategoryMixin, ServiceChatMixin, GroupedMessagesMixin, ContextMixin, DetailView):
    """Представление для отображения деталей услуги DonationService)."""

    title = "Обучение"
    model = DonationService
    template_name = "products/donation_detail.html"  # Путь к шаблону
    form_class = DonationServiceForm
    context_object_name = "service"

    def get_object(self):
        """Получает объект DonationService по ID или возвращает 404."""
        return get_object_or_404(DonationService, id=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        kwargs["slug"] = "donation"  # или динамически передавайте нужный слаг

        context = super().get_context_data(**kwargs)
        service = self.get_object()
        context["form"] = DonationServiceForm(instance=service)
        context["form_purchase"] = PurchaseForm()  # форма для покупки
        context["is_buyer"] = self.request.user != self.object.seller  # Проверка, покупатель ли это
        context["model_name"] = self.model._meta.model_name
        context["image_form"] = ServiceImageForm()  # Добавляем картинку
        context["images"] = self.object.images.all()
        context["seller_reviews"] = Review.objects.filter(seller=service.seller).order_by("-id")
        #  Получаем заказ с этим товаром и статусом "pending"
        # Только для авторизованных пользователей — проверка заказов
        if self.request.user.is_authenticated:
            pending_order = Order.objects.filter(
                content_type=ContentType.objects.get_for_model(service),
                object_id=service.id,
                user=self.request.user,
                status="pending",
            ).first()
        else:
            pending_order = None

        context["pending_order"] = pending_order
        return context

    def post(self, request, *args, **kwargs):
        service = self.get_object()

        # Проверка, что пользователь — продавец
        if service.seller != request.user:
            return HttpResponseForbidden("У вас нет прав на это действие.")
        # Удаление изображения
        if "delete_image" in request.POST:
            image_id = request.POST.get("image_id")
            image = get_object_or_404(service.images, id=image_id)
            image.delete()
            return redirect("products:donation_detail", pk=service.pk)

        # Добавление нового изображения
        if "add_image" in request.POST:
            if service.images.count() >= 4:
                context = self.get_context_data(object=service)
                context["image_limit_error"] = "Максимум 4 изображения разрешено."
                return self.render_to_response(context)
            image_form = ServiceImageForm(request.POST, request.FILES)
            if image_form.is_valid():
                new_img = image_form.save(commit=False)
                new_img.content_object = service
                new_img.save()
            return redirect("products:donation_detail", pk=service.pk)
        # Удаление
        if "delete" in request.POST:
            service.delete()
            return redirect("products:my_products")

        # Редактирование
        form = DonationServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect("products:donation_detail", pk=service.pk)

        # Если форма невалидна, отрисуем снова с ошибками
        context = self.get_context_data(object=service)
        context["form"] = form
        return self.render_to_response(context)


class GeneralServiceListView(CategoryMixin, ChatMixin, SearchDescriptionMixin, ContextMixin, PaginateMixin, ListView):
    """
    Вьюха для отображения списка услуг категории "Account".
    """

    title = "Услуги"
    model = GeneralService
    template_name = "products/services.html"  # Указываем путь к твоему шаблону
    context_object_name = "services"  # Имя переменной для доступа к данным в шаблоне

    def get_queryset(self):
        queryset = self.model.objects.all().order_by("id")
        user = self.request.user
        if user.is_authenticated:
            # Преобразуем ленивый объект в обычный
            print(f"🔐 Пользователь авторизован — исключаем его карточки: {user}")
            queryset = queryset.exclude(seller=user)
        else:
            print("🕵️ Пользователь анонимный — показываем все услуги")
        filter_form = GeneralServiceFilterForm(self.request.GET)
        if filter_form.is_valid():
            queryset = GeneralFilter(filter_form.cleaned_data, queryset=queryset, request=self.request).qs
        return queryset

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        kwargs["slug"] = "services"  # или динамически передавайте нужный слаг

        context = super().get_context_data(**kwargs)
        context["filter_form"] = GeneralServiceFilterForm(self.request.GET)
        context["form"] = GeneralServiceForm()
        return context

    def post(self, request, *args, **kwargs):
        form = GeneralServiceForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)  # Не сохраняем сразу, а создаем объект
            offer.seller = request.user  # Привязываем авторизованного пользователя как продавца
            form.save()  # Сохраняем данные формы
            return redirect("products:services")  # Здесь можно перенаправить на страницу успеха


class GeneralServiceDetailsView(CategoryMixin, ServiceChatMixin, GroupedMessagesMixin, ContextMixin, DetailView):
    """Представление для отображения деталей услуги (BattlePassService)."""

    title = "Обучение"
    model = GeneralService
    template_name = "products/services_detail.html"  # Путь к шаблону
    form_class = GeneralServiceForm
    context_object_name = "service"

    def get_object(self):
        """Получает объект BattlePassService по ID или возвращает 404."""
        return get_object_or_404(GeneralService, id=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        kwargs["slug"] = "services"  # или динамически передавайте нужный слаг

        context = super().get_context_data(**kwargs)
        service = self.get_object()
        context["form"] = GeneralServiceForm(instance=service)
        context["form_purchase"] = PurchaseForm()  # форма для покупки
        context["is_buyer"] = self.request.user != self.object.seller  # Проверка, покупатель ли это
        context["model_name"] = self.model._meta.model_name
        context["seller_reviews"] = Review.objects.filter(seller=service.seller).order_by("-id")
        #  Получаем заказ с этим товаром и статусом "pending"
        # Только для авторизованных пользователей — проверка заказов
        if self.request.user.is_authenticated:
            pending_order = Order.objects.filter(
                content_type=ContentType.objects.get_for_model(service),
                object_id=service.id,
                user=self.request.user,
                status="pending",
            ).first()
        else:
            pending_order = None

        context["pending_order"] = pending_order
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        service = self.get_object()

        # Проверка, что пользователь — продавец
        if service.seller != request.user:
            return HttpResponseForbidden("У вас нет прав на это действие.")

        # Удаление
        if "delete" in request.POST:
            service.delete()
            return redirect("products:my_products")

        # Редактирование
        form = GeneralServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect("products:services_detail", pk=service.pk)

        # Если форма невалидна, отрисуем снова с ошибками
        context = self.get_context_data(object=service)
        context["form"] = form
        return self.render_to_response(context)


class OtherServiceListView(CategoryMixin, ChatMixin, SearchDescriptionMixin, ContextMixin, PaginateMixin, ListView):
    """
    Вьюха для отображения списка услуг категории "Account".
    """

    title = "Прочее"
    model = OtherService
    template_name = "products/other.html"  # Указываем путь к твоему шаблону
    context_object_name = "services"  # Имя переменной для доступа к данным в шаблоне

    def get_queryset(self):
        queryset = self.model.objects.all().order_by("id")
        user = self.request.user
        if user.is_authenticated:
            # Преобразуем ленивый объект в обычный
            print(f"🔐 Пользователь авторизован — исключаем его карточки: {user}")
            queryset = queryset.exclude(seller=user)
        else:
            print("🕵️ Пользователь анонимный — показываем все услуги")
        filter_form = OtherServiceFilterForm(self.request.GET)
        if filter_form.is_valid():
            queryset = OtherFilter(filter_form.cleaned_data, queryset=queryset, request=self.request).qs
        return queryset

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        kwargs["slug"] = "other"  # или динамически передавайте нужный слаг

        context = super().get_context_data(**kwargs)
        context["filter_form"] = OtherServiceFilterForm(self.request.GET)
        context["form"] = OtherServiceForm()
        return context

    def post(self, request, *args, **kwargs):
        form = OtherServiceForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)  # Не сохраняем сразу, а создаем объект
            offer.seller = request.user  # Привязываем авторизованного пользователя как продавца
            form.save()  # Сохраняем данные формы
            return redirect("products:other")  # Здесь можно перенаправить на страницу успеха


class OtherServiceDetailsView(CategoryMixin, ServiceChatMixin, GroupedMessagesMixin, ContextMixin, DetailView):
    """Представление для отображения деталей услуги (OtherService)."""

    title = "Обучение"
    model = OtherService
    template_name = "products/other_detail.html"  # Путь к шаблону
    form_class = OtherServiceForm
    context_object_name = "service"

    def get_object(self):
        """Получает объект OtherService по ID или возвращает 404."""
        return get_object_or_404(OtherService, id=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        kwargs["slug"] = "other"  # или динамически передавайте нужный слаг

        context = super().get_context_data(**kwargs)
        service = self.get_object()
        context["form"] = OtherServiceForm(instance=service)
        context["form_purchase"] = PurchaseForm()  # форма для покупки
        context["is_buyer"] = self.request.user != self.object.seller  # Проверка, покупатель ли это
        context["model_name"] = self.model._meta.model_name
        context["seller_reviews"] = Review.objects.filter(seller=service.seller).order_by("-id")
        #  Получаем заказ с этим товаром и статусом "pending"
        # Только для авторизованных пользователей — проверка заказов
        if self.request.user.is_authenticated:
            pending_order = Order.objects.filter(
                content_type=ContentType.objects.get_for_model(service),
                object_id=service.id,
                user=self.request.user,
                status="pending",
            ).first()
        else:
            pending_order = None

        context["pending_order"] = pending_order
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        service = self.get_object()

        # Проверка, что пользователь — продавец
        if service.seller != request.user:
            return HttpResponseForbidden("У вас нет прав на это действие.")

        # Удаление
        if "delete" in request.POST:
            service.delete()
            return redirect("products:my_products")

        # Редактирование
        form = OtherServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect("products:other_detail", pk=service.pk)

        # Если форма невалидна, отрисуем снова с ошибками
        context = self.get_context_data(object=service)
        context["form"] = form
        return self.render_to_response(context)


class QualificationServiceListView(
    CategoryMixin, ChatMixin, SearchDescriptionMixin, ContextMixin, PaginateMixin, ListView
):
    """
    Вьюха для отображения списка услуг категории "Account".
    """

    title = "Квалификация"
    model = QualificationService
    template_name = "products/qualification.html"  # Указываем путь к твоему шаблону
    context_object_name = "services"  # Имя переменной для доступа к данным в шаблоне

    def get_queryset(self):
        queryset = self.model.objects.all().order_by("id")
        user = self.request.user
        if user.is_authenticated:
            # Преобразуем ленивый объект в обычный
            print(f"🔐 Пользователь авторизован — исключаем его карточки: {user}")
            queryset = queryset.exclude(seller=user)
        else:
            print("🕵️ Пользователь анонимный — показываем все услуги")
        filter_form = QualificationServiceFilterForm(self.request.GET)
        if filter_form.is_valid():
            queryset = QualificationFilter(filter_form.cleaned_data, queryset=queryset, request=self.request).qs
        return queryset

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        kwargs["slug"] = "qualification"  # или динамически передавайте нужный слаг

        context = super().get_context_data(**kwargs)
        context["filter_form"] = QualificationServiceFilterForm(self.request.GET)
        context["form"] = QualificationServiceForm()
        return context

    def post(self, request, *args, **kwargs):
        form = QualificationServiceForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)  # Не сохраняем сразу, а создаем объект
            offer.seller = request.user  # Привязываем авторизованного пользователя как продавца
            form.save()  # Сохраняем данные формы
            return redirect("products:qualification")  # Здесь можно перенаправить на страницу успеха


class QualificationServiceDetailsView(CategoryMixin, ServiceChatMixin, GroupedMessagesMixin, ContextMixin, DetailView):
    """Представление для отображения деталей услуги (BattlePassService)."""

    title = "Обучение"
    model = QualificationService
    template_name = "products/qualification_detail.html"  # Путь к шаблону
    form_class = QualificationServiceForm
    context_object_name = "service"

    def get_object(self):
        """Получает объект BattlePassService по ID или возвращает 404."""
        return get_object_or_404(QualificationService, id=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        kwargs["slug"] = "qualification"  # или динамически передавайте нужный слаг

        context = super().get_context_data(**kwargs)
        service = self.get_object()
        context["form"] = QualificationServiceForm(instance=service)
        context["form_purchase"] = PurchaseForm()  # форма для покупки
        context["is_buyer"] = self.request.user != self.object.seller  # Проверка, покупатель ли это
        context["model_name"] = self.model._meta.model_name
        context["seller_reviews"] = Review.objects.filter(seller=service.seller).order_by("-id")
        #  Получаем заказ с этим товаром и статусом "pending"
        # Только для авторизованных пользователей — проверка заказов
        if self.request.user.is_authenticated:
            pending_order = Order.objects.filter(
                content_type=ContentType.objects.get_for_model(service),
                object_id=service.id,
                user=self.request.user,
                status="pending",
            ).first()
        else:
            pending_order = None

        context["pending_order"] = pending_order
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        service = self.get_object()

        # Проверка, что пользователь — продавец
        if service.seller != request.user:
            return HttpResponseForbidden("У вас нет прав на это действие.")

        # Удаление
        if "delete" in request.POST:
            service.delete()
            return redirect("products:my_products")

        # Редактирование
        form = QualificationServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect("products:qualification_detail", pk=service.pk)

        # Если форма невалидна, отрисуем снова с ошибками
        context = self.get_context_data(object=service)
        context["form"] = form
        return self.render_to_response(context)


class MyProductsView(TemplateView):
    # Вьюха для отображения карточек в услугах(кроме своих)
    template_name = "products/my_products.html"

    def get_context_data(self, category_slug=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated:
            rp_services = RPService.objects.filter(seller=user)
            boost_services = BoostService.objects.filter(seller=user)
            battlepass_services = BattlePassService.objects.filter(seller=user)
            account_services = AccountService.objects.filter(seller=user)
            donation_services = DonationService.objects.filter(seller=user)
            other_services = OtherService.objects.filter(seller=user)
            qualification_services = QualificationService.objects.filter(seller=user)
            general_services = GeneralService.objects.filter(seller=user)
            training_services = TrainingService.objects.filter(seller=user)

            # Можно объединить в один список
            all_services = (
                list(rp_services)
                + list(boost_services)
                + list(battlepass_services)
                + list(account_services)
                + list(donation_services)
                + list(other_services)
                + list(qualification_services)
                + list(general_services)
                + list(training_services)
            )

            # Если нужно — отсортируй по дате
            all_services.sort(key=lambda s: s.created_at, reverse=True)  # если есть поле created_at

            context["services"] = all_services
            context["category_slug"] = category_slug
        else:
            context["services"] = []

        return context
