from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Category, ServerBasedService


class CategoryMixin:
    """
    Миксин для получения категории по slug и добавления ее в контекст.
    """

    def get_category(self, slug):
        try:
            category = Category.objects.get(slug=slug)
            return category
        except Category.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем слаг из URL или передаем его явно (например, для страницы AccountService)
        slug = kwargs.get("slug", None)

        if slug:
            category = self.get_category(slug)  # Получаем категорию по переданному слагу
            context["category"] = category

        # Получаем все категории для списка
        context["categories"] = Category.objects.all()

        return context


class ServerMixin:
    """
    Миксин для добавления информации о сервере в контекст.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем серверы для данного типа услуги
        context["servers"] = ServerBasedService.SERVER_CHOICES  # Передаем список всех серверов

        # Если текущая модель имеет поле server, передаем его значение
        # Например, если у нас есть конкретная услуга, связанная с сервером
        if hasattr(self, "object") and hasattr(self.object, "server"):
            context["selected_server"] = self.object.server

        return context


class SearchDescriptionMixin:
    """
    Миксин для обработки поиска и фильтров по полям `title`, `search_description`, а также других фильтров.
    """

    def get_search_query(self):
        """
        Возвращает строку запроса для поиска по полям `title` и `search_description`.
        """
        query = self.request.GET.get("q", "")
        return query.strip()

    def get_filters(self):
        """
        Возвращает фильтры из запроса.
        """
        filters = {
            "online_sellers": self.request.GET.get("online_sellers") == "on",  # Проверяем наличие фильтра
            "auto_delivery": self.request.GET.get("auto_delivery") == "on",
        }
        return filters

    def get_queryset(self):
        """
        Фильтрует объекты модели на основе запроса по полям `title`, `search_description` и дополнительных фильтров.
        """
        queryset = super().get_queryset()
        query = self.get_search_query()
        filters = self.get_filters()

        # Фильтрация по полям `title` и `search_description`
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(search_description__icontains=query)
            )

        # Применение фильтра "Только продавцы онлайн"
        if filters["online_sellers"]:
            queryset = queryset.filter(seller__is_online=True)

        # Применение фильтра "Автоматическая доставка"
        if filters["auto_delivery"]:
            queryset = queryset.filter(is_auto_delivery=True)

        return queryset
