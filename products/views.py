import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView

from chat.mixin import GroupedMessagesMixin
from common.views import ContextMixin
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
    PaginateMixin,
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
    TrainingService,
)


# Create your views here.
logger = logging.getLogger(__name__)
MAX_IMAGES_PER_SERVICE = 4
SERVICE_MODELS = [
    RPService,
    BoostService,
    BattlePassService,
    AccountService,
    DonationService,
    OtherService,
    QualificationService,
    GeneralService,
    TrainingService,
]


class CategoryView(View):
    model = Category
    title = 'Услуги'
    template_name = 'products/products.html'
    context_object_name = 'categories'
    background_image = '/static/deps/images/SB_Riven.jpg'

    def get(self, request, slug=None):
        if slug:
            # Если слаг передан, получаем соответствующую категорию
            category = get_object_or_404(Category, slug=slug)
            return render(
                request,
                self.template_name,
                {
                    'categories': category,
                    'title': self.title,
                },
            )


class BaseServiceDetailView(
    CategoryMixin, ServiceChatMixin, GroupedMessagesMixin, ContextMixin, DetailView
):
    context_object_name = 'service'
    title = ''
    slug = ''

    def get_object(self):
        """Получает объект AccountService по ID или возвращает 404."""
        qs = self.model.objects.select_related('seller', 'category')
        has_images_field = any(f.name == 'images' for f in self.model._meta.get_fields())
        if has_images_field:
            qs = qs.prefetch_related('images')
        return get_object_or_404(qs, id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        kwargs['slug'] = self.slug  # или динамически передавайте нужный слаг
        context = super().get_context_data(**kwargs)
        service = self.object
        context['form'] = self.form_class(instance=service)
        context['form_purchase'] = PurchaseForm()  # форма для покупки
        context['is_buyer'] = self.request.user != service.seller  # Проверка, покупатель ли это
        context['model_name'] = self.model._meta.model_name
        context['seller_reviews'] = Review.objects.filter(seller=service.seller).order_by('-id')
        # Только для авторизованных пользователей — проверка заказов
        if self.request.user.is_authenticated:
            pending_order = Order.objects.filter(
                content_type=ContentType.objects.get_for_model(service),
                object_id=service.id,
                user=self.request.user,
                status='pending',
            ).first()
        else:
            pending_order = None

        context['pending_order'] = pending_order
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        service = self.object
        # Проверка, что пользователь — продавец
        if not self.can_edit(service, request.user):
            return JsonResponse(
                {'success': False, 'message': 'У вас нет прав на это действие.'}, status=403
            )
        # Удаление
        if 'delete' in request.POST:
            service.delete()
            return redirect('products:my_products')
        # Редактирование
        elif 'edit_service' in request.POST:
            return self.edit_service(request.POST, request.FILES, service)
        # Удаление изображения
        elif 'delete_image' in request.POST and self.has_images():
            image_id = request.POST.get('image_id')
            if not image_id:  # если не передали id
                return JsonResponse({'success': False, 'message': 'image_id обязателен'}, status=400)
            success = self.delete_image(image_id)
            if success:
                return JsonResponse({'success': True, 'message': 'Изображение удалено.'})
            return JsonResponse({'success': False, 'message': 'Ошибка при удалении изображения.'})
        # Добавление нового изображения
        elif 'add_image' in request.POST and self.has_images():
            result = self.add_image(request.POST, request.FILES)
            return JsonResponse(result)
        else:
            return JsonResponse({'success': False, 'message': 'Неизвестное действие'}, status=400)

    def can_edit(self, service, user) -> bool:
        return getattr(user, 'is_authenticated', False) and service.seller_id == getattr(
            user, 'id', None
        )

    def has_images(self):
        return any(f.name == 'images' for f in self.model._meta.get_fields())

    def get_images(self):
        if self.has_images():
            return self.object.images.all()
        else:
            return []

    def delete_image(self, image_id):
        """Удаляет изображение по ID, если есть."""
        img = self.object.images.filter(id=image_id).first()
        if not img:
            return False
        img.delete()
        return True

    def add_image(self, post_data, files_data):
        if self.has_images():
            if self.object.images.count() >= MAX_IMAGES_PER_SERVICE:
                return {'success': False, 'message': 'Максимум 4 изображения разрешено.'}
            image_form = ServiceImageForm(post_data, files_data)
            if image_form.is_valid():
                new_img = image_form.save(commit=False)
                new_img.content_object = self.object
                new_img.save()
                return {'success': True, 'message': 'Изображение добавлено.'}
            return {
                'success': False,
                'message': 'Ошибка при загрузке изображения.',
                'errors': image_form.errors.as_json(),
            }

    def edit_service(self, post_data, files_data, service):
        form = self.form_class(post_data, files_data, instance=service)

        if form.is_valid():
            form.save()
            return redirect(self.request.path)
        context = self.get_context_data(object=service)
        context['form'] = form
        return self.render_to_response(context)


class BaseServiceListView(CategoryMixin, ChatMixin, ContextMixin, PaginateMixin, ListView):
    context_object_name = 'services'
    filter_form_class = None
    create_form_class = None

    def get_queryset(self):
        # Получаем все услуги (карточки) для текущего пользователя
        queryset = self.model.objects.filter(is_active=True).select_related('seller', 'category')
        if any(f.name == 'images' for f in self.model._meta.get_fields()):
            queryset = queryset.prefetch_related('images')
        queryset = queryset.order_by('id')

        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.exclude(seller=self.request.user)

        if self.filter_form_class:
            filter_form = self.filter_form_class(self.request.GET)
            if filter_form.is_valid():
                queryset = self.filter(
                    filter_form.cleaned_data, queryset=queryset, request=self.request
                ).qs

        return queryset

    def get_context_data(self, **kwargs):  # для передачи контекста в шаблон
        kwargs['slug'] = self.slug
        context = super().get_context_data(**kwargs)
        context['filter_form'] = self.filter_form_class(self.request.GET)
        context['form'] = self.create_form_class()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        form = self.create_form_class(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)  # Не сохраняем сразу, а создаем объект
            offer.seller = request.user  # Привязываем авторизованного пользователя как продавца
            offer.save()  # Сохраняем данные формы
            # Обработка загруженных файлов (картинок)
            if self.has_images() and 'image' in request.FILES:
                image_form = ServiceImageForm(request.POST, request.FILES)
                if image_form.is_valid() and image_form.cleaned_data.get('image'):
                    image = image_form.save(commit=False)
                    image.content_object = offer  # Связываем картинку с сервисом
                    image.save()
            return redirect(self.request.path)  # Здесь можно перенаправить на страницу успеха

        # Добавление ошибок в лог или отладочную информацию
        # Логируем ошибки
        logger.error(f'Ошибка в форме: {form.errors}')
        return self.get(request, *args, **kwargs)  # Возвращаем форму с ошибками

    def has_images(self):
        return any(f.name == 'images' for f in self.model._meta.get_fields())


class AccountServiceListView(BaseServiceListView):
    """
    Вьюха для отображения списка услуг категории "Account".
    """

    title = 'Аккаунты'
    model = AccountService
    filter = AccountFilter
    filter_form_class = AccountServiceFilterForm
    template_name = 'products/account.html'
    create_form_class = AccountServiceForm
    slug = 'accounts'

    def get_context_data(self, **kwargs):  # для передачи контекста в шаблон
        context = super().get_context_data(**kwargs)
        context['image_form'] = ServiceImageForm()  # Добавляем форму для загрузки картинки
        return context


class AccountServiceDetailView(BaseServiceDetailView):
    title = 'Покупка Аккунта'
    model = AccountService
    template_name = 'products/account_detail.html'  # Путь к шаблону
    form_class = AccountServiceForm
    slug = 'accounts'

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        context = super().get_context_data(**kwargs)
        context['image_form'] = ServiceImageForm()  # Добавляем картинку
        context['images'] = self.get_images()
        return context


class RPServiceListView(BaseServiceListView):
    title = 'RP'
    model = RPService
    filter = RpFilter
    filter_form_class = RPServiceFilterForm
    create_form_class = RPServiceForm
    template_name = 'products/riot-points.html'  # Указываем путь к твоему шаблону
    slug = 'riot-points'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(quantity__gt=0)


class RPServiceDetailView(
    BaseServiceDetailView,
):
    """Представление для отображения деталей услуги (RPService)."""

    title = 'Покупка RP'
    model = RPService
    template_name = 'products/riot-points_detail.html'  # Путь к шаблону
    form_class = RPServiceForm
    slug = 'riot-points'


class BoostServiceListView(BaseServiceListView):
    """
    Вьюха для отображения списка услуг категории "Boost".
    """

    title = 'Буст'
    model = BoostService
    filter = BoostFilter
    filter_form_class = BoostServiceFilterForm
    create_form_class = BoostServiceForm
    slug = 'boosting'
    template_name = 'products/boost.html'  # Указываем путь к твоему шаблону


class BoostServiceDetailsView(BaseServiceDetailView):
    """Представление для отображения деталей услуги (RPService)."""

    title = 'Буст аккаунта'
    model = BoostService
    template_name = 'products/boost_detail.html'  # Путь к шаблону
    form_class = BoostServiceForm
    slug = 'boosting'


class TrainingServiceListView(BaseServiceListView):
    title = 'Обучение'
    model = TrainingService
    filter = TrainingFilter
    filter_form_class = TrainingServiceFilterForm
    create_form_class = TrainingServiceForm
    template_name = 'products/training.html'  # Указываем путь к твоему шаблону
    slug = 'training'


class TrainingServiceDetailsView(BaseServiceDetailView):
    """Представление для отображения деталей услуги (TrainingService)."""

    title = 'Обучение'
    model = TrainingService
    template_name = 'products/training_detail.html'  # Путь к шаблону
    form_class = TrainingServiceForm
    slug = 'training'


class BattlePassServiceListView(BaseServiceListView):
    title = 'Боевой пропуск'
    model = BattlePassService
    filter = BattlePassFilter
    filter_form_class = BattlePassServiceFilterForm
    create_form_class = BattlePassServiceForm
    template_name = 'products/battlepass.html'  # Указываем путь к твоему шаблону
    slug = 'battle-pass'


class BattlePassServiceDetailsView(BaseServiceDetailView):
    """Представление для отображения деталей услуги (BattlePassService)."""

    title = 'Обучение'
    model = BattlePassService
    template_name = 'products/battlepass_detail.html'  # Путь к шаблону
    form_class = BattlePassServiceForm
    slug = 'battle-pass'


class DonationServiceListView(BaseServiceListView):
    title = 'Донат'
    model = DonationService
    filter = DonationFilter
    filter_form_class = DonationServiceFilterForm
    create_form_class = DonationServiceForm
    template_name = 'products/donation.html'  # Указываем путь к твоему шаблону
    slug = 'donation'

    def get_context_data(self, **kwargs):  # для передачи контекста в шаблон
        context = super().get_context_data(**kwargs)
        context['image_form'] = ServiceImageForm()  # Добавляем форму для загрузки картинки
        return context


class DonationServiceDetailsView(BaseServiceDetailView):
    """Представление для отображения деталей услуги DonationService)."""

    title = 'Обучение'
    model = DonationService
    template_name = 'products/donation_detail.html'  # Путь к шаблону
    form_class = DonationServiceForm
    slug = 'donation'

    def get_context_data(self, **kwargs):
        # Сюда передаем slug, чтобы миксин мог правильно его обработать
        context = super().get_context_data(**kwargs)
        context['image_form'] = ServiceImageForm()  # Добавляем картинку
        context['images'] = self.get_images()
        return context


class GeneralServiceListView(BaseServiceListView):
    title = 'Услуги'
    model = GeneralService
    filter = GeneralFilter
    filter_form_class = GeneralServiceFilterForm
    create_form_class = GeneralServiceForm
    template_name = 'products/services.html'
    slug = 'services'


class GeneralServiceDetailsView(BaseServiceDetailView):
    """Представление для отображения деталей услуги (BattlePassService)."""

    title = 'Обучение'
    model = GeneralService
    template_name = 'products/services_detail.html'  # Путь к шаблону
    form_class = GeneralServiceForm
    slug = 'services'


class OtherServiceListView(BaseServiceListView):
    title = 'Прочее'
    model = OtherService
    filter = OtherFilter
    filter_form_class = OtherServiceFilterForm
    create_form_class = OtherServiceForm
    template_name = 'products/other.html'  # Указываем путь к твоему шаблону
    slug = 'other'


class OtherServiceDetailsView(BaseServiceDetailView):
    """Представление для отображения деталей услуги (OtherService)."""

    title = 'Обучение'
    model = OtherService
    template_name = 'products/other_detail.html'  # Путь к шаблону
    form_class = OtherServiceForm
    slug = 'other'


class QualificationServiceListView(BaseServiceListView):
    """
    Вьюха для отображения списка услуг категории "Account".
    """

    title = 'Квалификация'
    model = QualificationService
    filter = QualificationFilter
    filter_form_class = QualificationServiceFilterForm
    create_form_class = QualificationServiceForm
    template_name = 'products/qualification.html'  # Указываем путь к твоему шаблону
    slug = 'qualification'


class QualificationServiceDetailsView(BaseServiceDetailView):
    """Представление для отображения деталей услуги (BattlePassService)."""

    title = 'Обучение'
    model = QualificationService
    template_name = 'products/qualification_detail.html'  # Путь к шаблону
    form_class = QualificationServiceForm
    slug = 'qualification'


class MyProductsView(LoginRequiredMixin, ContextMixin, TemplateView):
    # Вьюха для отображения карточек в услугах(кроме своих)
    template_name = 'products/my_products.html'
    title = 'Мои продукты'
    login_url = 'users:authorization'
    background_image = '/static/deps/images/SB_Riven.jpg'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        category_slug = kwargs.get('category_slug')
        all_services = []

        for M in SERVICE_MODELS:
            qs = M.objects.filter(seller=user).select_related('seller', 'category')

            # если есть поле images — подгружаем
            if any(f.name == 'images' for f in M._meta.get_fields()):
                qs = qs.prefetch_related('images')

            # если есть поле quantity — фильтруем по > 0
            if any(f.name == 'quantity' for f in M._meta.get_fields()):
                qs = qs.filter(quantity__gt=0)

            all_services.extend(qs)

        # Если нужно — отсортируй по дате
        all_services.sort(key=lambda s: s.created_at, reverse=True)  # если есть поле created_at

        context['services'] = all_services
        context['category_slug'] = category_slug
        return context
