import django_filters

from products.models import RPService


class RpFilter(django_filters.FilterSet):
    is_auto_delivery = django_filters.BooleanFilter(method="filter_auto_delivery")
    seller_is_online = django_filters.BooleanFilter(method="filter_seller_online")

    def filter_auto_delivery(self, queryset, name, value):
        if value:  # Если чекбокс включен
            return queryset.filter(is_auto_delivery=True)
        return queryset

    def filter_seller_online(self, queryset, name, value):
        if value:  # Если чекбокс включен
            return queryset.filter(seller_is_online=True)
        return queryset

    class Meta:
        model = RPService
        fields = ["server", "filter_type", "seller_is_online", "is_auto_delivery"]
