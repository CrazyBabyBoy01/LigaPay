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
    """
    Отображает страницу категории услуг по её slug.
    Если slug отсутствует, выполняет редирект на главную страницу.
    """

    model = Category
    title = 'Услуги'
    template_name = 'products/products.html'
    context_object_name = 'categories'
    background_image = '/static/deps/images/SB_Riven.jpg'

    def get(self, request, slug=None):
        if slug:
            category = get_object_or_404(Category, slug=slug)
            return render(
                request,
                self.template_name,
                {
                    'categories': category,
                    'title': self.title,
                },
            )
        return redirect('main:index')


class BaseServiceDetailView(
    CategoryMixin, ServiceChatMixin, GroupedMessagesMixin, ContextMixin, DetailView
):
    """
    Базовое представление для отображения детальной информации об услуге.

    Реализует:
    - получение объекта услуги с предзагрузкой связанных данных (продавец, категория, изображения);
    - формирование контекста с формами покупки и редактирования;
    - обработку POST-запросов: редактирование, удаление услуги и управление изображениями.
    """

    context_object_name = 'service'
    title = ''
    slug = ''

    def get_object(self):
        """Получает объект или возвращает 404."""
        qs = self.model.objects.select_related('seller', 'category')
        has_images_field = any(f.name == 'images' for f in self.model._meta.get_fields())
        if has_images_field:
            qs = qs.prefetch_related('images')
        return get_object_or_404(qs, id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        kwargs['slug'] = self.slug
        context = super().get_context_data(**kwargs)
        service = self.object
        context['form'] = self.form_class(instance=service)
        context['form_purchase'] = PurchaseForm()
        context['is_buyer'] = self.request.user != service.seller
        context['model_name'] = self.model._meta.model_name
        context['seller_reviews'] = Review.objects.filter(seller=service.seller).order_by('-id')
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
        if not self.can_edit(service, request.user):
            return JsonResponse(
                {'success': False, 'message': 'У вас нет прав на это действие.'}, status=403
            )

        if 'delete' in request.POST:
            service.delete()
            return redirect('products:my_products')

        if 'edit_service' in request.POST:
            return self.edit_service(request.POST, request.FILES, service)

        if 'delete_image' in request.POST and self.has_images():
            image_id = request.POST.get('image_id')
            if not image_id:
                return JsonResponse({'success': False, 'message': 'image_id обязателен'}, status=400)
            success = self.delete_image(image_id)
            if success:
                return JsonResponse({'success': True, 'message': 'Изображение удалено.'})
            return JsonResponse({'success': False, 'message': 'Ошибка при удалении изображения.'})

        if 'add_image' in request.POST and self.has_images():
            result = self.add_image(request.POST, request.FILES)
            return JsonResponse(result)
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
    """
    Базовое представление для отображения списка услуг.

    Реализует:
    - получение queryset активных услуг с фильтрацией по форме;
    - исключение услуг текущего пользователя;
    - создание новой услуги через POST-запрос (с изображениями);
    - передачу форм в контекст.
    """

    context_object_name = 'services'
    filter_form_class = None
    create_form_class = None

    def get_queryset(self):
        queryset = self.model.objects.filter(is_active=True)

        model_fields = {field.name for field in self.model._meta.get_fields()}

        if 'quantity' in model_fields:
            queryset = queryset.filter(quantity__gt=0)

        queryset = queryset.select_related('seller', 'category')

        if 'images' in model_fields:
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

    def get_context_data(self, **kwargs):
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
            offer = form.save(commit=False)
            offer.seller = request.user
            offer.save()

            if self.has_images() and 'image' in request.FILES:
                image_form = ServiceImageForm(request.POST, request.FILES)
                if image_form.is_valid() and image_form.cleaned_data.get('image'):
                    image = image_form.save(commit=False)
                    image.content_object = offer
                    image.save()
            return redirect(self.request.path)

        logger.error(f'Ошибка в форме: {form.errors}')
        return self.get(request, *args, **kwargs)

    def has_images(self):
        return any(f.name == 'images' for f in self.model._meta.get_fields())


class AccountServiceListView(BaseServiceListView):
    """
    Представление списка услуг категории «Аккаунты».
    """

    title = 'Аккаунты'
    model = AccountService
    filter = AccountFilter
    filter_form_class = AccountServiceFilterForm
    template_name = 'products/account.html'
    create_form_class = AccountServiceForm
    slug = 'accounts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['image_form'] = ServiceImageForm()
        return context


class AccountServiceDetailView(BaseServiceDetailView):
    """
    Представление деталей услуги категории «Аккаунты».
    """

    title = 'Покупка Аккунта'
    model = AccountService
    template_name = 'products/account_detail.html'
    form_class = AccountServiceForm
    slug = 'accounts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['image_form'] = ServiceImageForm()
        context['images'] = self.get_images()
        return context


class RPServiceListView(BaseServiceListView):
    """
    Представление списка услуг категории «RP».
    """

    title = 'RP'
    model = RPService
    filter = RpFilter
    filter_form_class = RPServiceFilterForm
    create_form_class = RPServiceForm
    template_name = 'products/riot-points.html'
    slug = 'riot-points'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(quantity__gt=0)


class RPServiceDetailView(
    BaseServiceDetailView,
):
    """
    Представление деталей услуги категории «RP».
    """

    title = 'Покупка RP'
    model = RPService
    template_name = 'products/riot-points_detail.html'
    form_class = RPServiceForm
    slug = 'riot-points'


class BoostServiceListView(BaseServiceListView):
    """
    Представление списка услуг категории «Буст».
    """

    title = 'Буст'
    model = BoostService
    filter = BoostFilter
    filter_form_class = BoostServiceFilterForm
    create_form_class = BoostServiceForm
    slug = 'boosting'
    template_name = 'products/boost.html'


class BoostServiceDetailsView(BaseServiceDetailView):
    """
    Представление деталей услуги категории «Буст».
    """

    title = 'Буст'
    model = BoostService
    template_name = 'products/boost_detail.html'
    form_class = BoostServiceForm
    slug = 'boosting'


class TrainingServiceListView(BaseServiceListView):
    """
    Представление списка услуг категории «Обучение».
    """

    title = 'Обучение'
    model = TrainingService
    filter = TrainingFilter
    filter_form_class = TrainingServiceFilterForm
    create_form_class = TrainingServiceForm
    template_name = 'products/training.html'
    slug = 'training'


class TrainingServiceDetailsView(BaseServiceDetailView):
    """
    Представление деталей услуги категории «Обучение».
    """

    title = 'Обучение'
    model = TrainingService
    template_name = 'products/training_detail.html'
    form_class = TrainingServiceForm
    slug = 'training'


class BattlePassServiceListView(BaseServiceListView):
    """
    Представление списка услуг категории «Боевой пропуск».
    """

    title = 'Боевой пропуск'
    model = BattlePassService
    filter = BattlePassFilter
    filter_form_class = BattlePassServiceFilterForm
    create_form_class = BattlePassServiceForm
    template_name = 'products/battlepass.html'
    slug = 'battle-pass'


class BattlePassServiceDetailsView(BaseServiceDetailView):
    """
    Представление деталей услуги категории «Боевой пропуск».
    """

    title = 'Боевой пропуск'
    model = BattlePassService
    template_name = 'products/battlepass_detail.html'
    form_class = BattlePassServiceForm
    slug = 'battle-pass'


class DonationServiceListView(BaseServiceListView):
    """
    Представление списка услуг категории «Донат».
    """

    title = 'Донат'
    model = DonationService
    filter = DonationFilter
    filter_form_class = DonationServiceFilterForm
    create_form_class = DonationServiceForm
    template_name = 'products/donation.html'
    slug = 'donation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['image_form'] = ServiceImageForm()
        return context


class DonationServiceDetailsView(BaseServiceDetailView):
    """
    Представление деталей услуги категории «Донат».
    """

    title = 'Донат'
    model = DonationService
    template_name = 'products/donation_detail.html'
    form_class = DonationServiceForm
    slug = 'donation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['image_form'] = ServiceImageForm()
        context['images'] = self.get_images()
        return context


class GeneralServiceListView(BaseServiceListView):
    """
    Представление списка услуг категории «Услуги».
    """

    title = 'Услуги'
    model = GeneralService
    filter = GeneralFilter
    filter_form_class = GeneralServiceFilterForm
    create_form_class = GeneralServiceForm
    template_name = 'products/services.html'
    slug = 'services'


class GeneralServiceDetailsView(BaseServiceDetailView):
    """
    Представление деталей услуги категории «Услуги».
    """

    title = 'Услуги'
    model = GeneralService
    template_name = 'products/services_detail.html'
    form_class = GeneralServiceForm
    slug = 'services'


class OtherServiceListView(BaseServiceListView):
    """
    Представление списка услуг категории «Прочее».
    """

    title = 'Прочее'
    model = OtherService
    filter = OtherFilter
    filter_form_class = OtherServiceFilterForm
    create_form_class = OtherServiceForm
    template_name = 'products/other.html'  # Указываем путь к твоему шаблону
    slug = 'other'


class OtherServiceDetailsView(BaseServiceDetailView):
    """
    Представление деталей услуги категории «Обучение».
    """

    title = 'Обучение'
    model = OtherService
    template_name = 'products/other_detail.html'  # Путь к шаблону
    form_class = OtherServiceForm
    slug = 'other'


class QualificationServiceListView(BaseServiceListView):
    """
    Представление списка услуг категории «Квалификация».
    """

    title = 'Квалификация'
    model = QualificationService
    filter = QualificationFilter
    filter_form_class = QualificationServiceFilterForm
    create_form_class = QualificationServiceForm
    template_name = 'products/qualification.html'  # Указываем путь к твоему шаблону
    slug = 'qualification'


class QualificationServiceDetailsView(BaseServiceDetailView):
    """
    Представление деталей услуги категории «Обучение».
    """

    title = 'Обучение'
    model = QualificationService
    template_name = 'products/qualification_detail.html'  # Путь к шаблону
    form_class = QualificationServiceForm
    slug = 'qualification'


class MyProductsView(LoginRequiredMixin, ContextMixin, TemplateView):
    """
    Отображает все услуги, созданные текущим пользователем.

    Собирает объекты из всех моделей услуг (Account, RP, Boost и др.),
    фильтрует по продавцу и сортирует по дате создания.
    """

    template_name = 'products/my_products.html'
    title = 'Мои продукты'
    login_url = 'users:authorization'
    background_image = '/static/deps/images/SB_Riven.jpg'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        category_slug = kwargs.get('category_slug')
        all_services = []

        for m in SERVICE_MODELS:
            qs = m.objects.filter(seller=user).select_related('seller', 'category')

            if any(f.name == 'images' for f in m._meta.get_fields()):
                qs = qs.prefetch_related('images')

            if any(f.name == 'quantity' for f in m._meta.get_fields()):
                qs = qs.filter(quantity__gt=0)

            all_services.extend(qs)

        all_services.sort(key=lambda s: s.created_at, reverse=True)

        context['services'] = all_services
        context['category_slug'] = category_slug
        return context
