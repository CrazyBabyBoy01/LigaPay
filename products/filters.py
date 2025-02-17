import django_filters
from attr import fields
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


class RpFilter(django_filters.FilterSet):
    is_auto_delivery = django_filters.BooleanFilter(method="filter_auto_delivery")
    seller_is_online = django_filters.BooleanFilter(method="filter_seller_online")

    def filter_auto_delivery(self, queryset, name, value):
        if value:  # Если чекбокс включен
            return queryset.filter(is_auto_delivery=True)
        return queryset

    def filter_seller_online(self, queryset, name, value):
        if value:  # Если чекбокс включен
            return queryset.filter(seller__last_activity__gte=now() - timedelta(minutes=5))
        return queryset

    class Meta:
        model = RPService
        fields = ["server", "filter_type", "seller_is_online", "is_auto_delivery"]


class AccountFilter(django_filters.FilterSet):
    is_auto_delivery = django_filters.BooleanFilter(method="filter_auto_delivery")
    seller_is_online = django_filters.BooleanFilter(method="filter_seller_online")
    character_count = django_filters.RangeFilter()
    account_level = django_filters.RangeFilter()
    skin_count = django_filters.RangeFilter()
    search = django_filters.CharFilter(method="filter_search", label="Поиск")

    def filter_auto_delivery(self, queryset, name, value):
        if value:  # Если чекбокс включен
            return queryset.filter(is_auto_delivery=True)
        return queryset

    def filter_seller_online(self, queryset, name, value):
        if value:  # Если чекбокс включен
            return queryset.filter(seller__last_activity__gte=now() - timedelta(minutes=5))
        return queryset

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(title__icontains=value) | Q(description__icontains=value))

    class Meta:
        model = AccountService
        fields = [
            "server",
            "filter_type",
            "rank",
            "seller_is_online",
            "is_auto_delivery",
            "search",
            "character_count",
            "account_level",
            "skin_count",
        ]


class BoostFilter(django_filters.FilterSet):
    seller_is_online = django_filters.BooleanFilter(method="filter_seller_online")
    search = django_filters.CharFilter(method="filter_search", label="Поиск")
    server = django_filters.CharFilter()

    def filter_seller_online(self, queryset, name, value):
        if value:  # Если чекбокс включен
            return queryset.filter(seller__last_activity__gte=now() - timedelta(minutes=5))
        return queryset

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(title__icontains=value) | Q(description__icontains=value))

    class Meta:
        model = BoostService

        fields = ["filter_type", "seller_is_online", "rank_range", "search"]


class TrainingFilter(django_filters.FilterSet):
    seller_is_online = django_filters.BooleanFilter(method="filter_seller_online")
    search = django_filters.CharFilter(method="filter_search", label="Поиск")

    def filter_seller_online(self, queryset, name, value):
        if value:  # Если чекбокс включен
            return queryset.filter(seller__last_activity__gte=now() - timedelta(minutes=5))
        return queryset

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(title__icontains=value) | Q(description__icontains=value))

    class Meta:
        model = TrainingService
        fields = ["filter_type", "seller_is_online", "search"]


class BattlePassFilter(django_filters.FilterSet):
    is_auto_delivery = django_filters.BooleanFilter(method="filter_auto_delivery")
    seller_is_online = django_filters.BooleanFilter(method="filter_seller_online")

    def filter_auto_delivery(self, queryset, name, value):
        if value:  # Если чекбокс включен
            return queryset.filter(is_auto_delivery=True)
        return queryset

    def filter_seller_online(self, queryset, name, value):
        if value:  # Если чекбокс включен
            return queryset.filter(seller__last_activity__gte=now() - timedelta(minutes=5))
        return queryset

    class Meta:
        model = BattlePassService
        fields = ["server", "filter_type", "seller_is_online", "is_auto_delivery"]


class DonationFilter(django_filters.FilterSet):
    is_auto_delivery = django_filters.BooleanFilter(method="filter_auto_delivery")
    seller_is_online = django_filters.BooleanFilter(method="filter_seller_online")
    search = django_filters.CharFilter(method="filter_search", label="Поиск")

    def filter_auto_delivery(self, queryset, name, value):
        if value:  # Если чекбокс включен
            return queryset.filter(is_auto_delivery=True)
        return queryset

    def filter_seller_online(self, queryset, name, value):
        if value:  # Если чекбокс включен
            return queryset.filter(seller__last_activity__gte=now() - timedelta(minutes=5))
        return queryset

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(title__icontains=value) | Q(description__icontains=value))

    class Meta:
        model = DonationService
        fields = ["server", "filter_type", "seller_is_online", "is_auto_delivery", "receiving_method", "search"]


class GeneralFilter(django_filters.FilterSet):
    seller_is_online = django_filters.BooleanFilter(method="filter_seller_online")
    search = django_filters.CharFilter(method="filter_search", label="Поиск")

    def filter_seller_online(self, queryset, name, value):
        if value:  # Если чекбокс включен
            return queryset.filter(seller__last_activity__gte=now() - timedelta(minutes=5))
        return queryset

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(title__icontains=value) | Q(description__icontains=value))

    class Meta:
        model = GeneralService
        fields = ["filter_type", "seller_is_online", "search"]


class QualificationFilter(django_filters.FilterSet):
    seller_is_online = django_filters.BooleanFilter(method="filter_seller_online")
    search = django_filters.CharFilter(method="filter_search", label="Поиск")

    def filter_seller_online(self, queryset, name, value):
        if value:  # Если чекбокс включен
            return queryset.filter(seller__last_activity__gte=now() - timedelta(minutes=5))
        return queryset

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(title__icontains=value) | Q(description__icontains=value))

    class Meta:
        model = QualificationService
        fields = ["server", "seller_is_online", "search"]


class OtherFilter(django_filters.FilterSet):
    is_auto_delivery = django_filters.BooleanFilter(method="filter_auto_delivery")
    seller_is_online = django_filters.BooleanFilter(method="filter_seller_online")
    search = django_filters.CharFilter(method="filter_search", label="Поиск")

    def filter_auto_delivery(self, queryset, name, value):
        if value:  # Если чекбокс включен
            return queryset.filter(is_auto_delivery=True)
        return queryset

    def filter_seller_online(self, queryset, name, value):
        if value:  # Если чекбокс включен
            return queryset.filter(seller__last_activity__gte=now() - timedelta(minutes=5))
        return queryset

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(title__icontains=value) | Q(description__icontains=value))

    class Meta:
        model = OtherService
        fields = ["seller_is_online", "is_auto_delivery", "search", "filter_type"]
