import django_filters
from django.conf import settings
from django.db.models import Q
from django.utils.timezone import now, timedelta

from products.models import (
    AccountService,
    BattlePassService,
    BoostService,
    DonationService,
    GeneralService,
    OtherService,
    QualificationService,
    RPService,
    TrainingService,
)


class BaseServiceFilter(django_filters.FilterSet):
    """
    Базовый фильтр для моделей, наследующих BaseService.

    Предоставляет общие фильтры:
      - q — текстовый поиск по названию, описанию и полю search_description;
      - is_auto_delivery — фильтрация услуг с автоматической выдачей;
      - seller_is_online — фильтрация по активности продавца за последние N минут.

    Этот фильтр используется как родитель для конкретных фильтров услуг (например, AccountFilter,
    RpFilter и др.).
    обеспечивая единообразную логику поиска и стандартные фильтры для всех категорий.
    """

    q = django_filters.CharFilter(method='filter_q', label='Поиск')
    is_auto_delivery = django_filters.BooleanFilter(method='filter_auto_delivery')
    seller_is_online = django_filters.BooleanFilter(method='filter_seller_online')

    def filter_q(self, queryset, name, value):
        value = (value or '').strip()
        if value:
            return queryset.filter(
                Q(title__icontains=value)
                | Q(description__icontains=value)
                | Q(search_description__icontains=value)
            )
        return queryset

    def filter_auto_delivery(self, queryset, name, value):
        if value is True:
            return queryset.filter(is_auto_delivery=True)
        return queryset

    def filter_seller_online(self, queryset, name, value):
        if value is True:  # Если чекбокс включен
            return queryset.filter(
                seller__last_activity__gte=now() - timedelta(minutes=settings.USER_ONLINE_MINUTES)
            )
        return queryset


class AccountFilter(BaseServiceFilter):
    character_count = django_filters.RangeFilter()
    account_level = django_filters.RangeFilter()
    skin_count = django_filters.RangeFilter()

    class Meta:
        model = AccountService
        fields = [
            'server',
            'filter_type',
            'rank',
            'character_count',
            'account_level',
            'skin_count',
        ]


class RpFilter(BaseServiceFilter):
    class Meta:
        model = RPService
        fields = ['server', 'filter_type']


class BoostFilter(BaseServiceFilter):
    class Meta:
        model = BoostService
        fields = ['filter_type', 'server', 'rank_range']


class TrainingFilter(BaseServiceFilter):
    class Meta:
        model = TrainingService
        fields = ['filter_type']


class BattlePassFilter(BaseServiceFilter):
    class Meta:
        model = BattlePassService
        fields = ['server', 'filter_type']


class DonationFilter(BaseServiceFilter):
    class Meta:
        model = DonationService
        fields = [
            'server',
            'filter_type',
            'receiving_method',
        ]


class GeneralFilter(BaseServiceFilter):
    class Meta:
        model = GeneralService
        fields = ['filter_type']


class QualificationFilter(BaseServiceFilter):
    class Meta:
        model = QualificationService
        fields = ['server']


class OtherFilter(BaseServiceFilter):
    class Meta:
        model = OtherService
        fields = ['filter_type']
