from chat.models import ChatMessage
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Category, ServerBasedService


class CategoryMixin:
    """
    Миксин для получения категории по slug и добавления ее в контекст.
    """

    def get_category(self, slug):
        try:
            return Category.objects.get(slug=slug)
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


class PaginateMixin:
    paginate_by = 3


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
            queryset = queryset.filter(Q(title__icontains=query) | Q(search_description__icontains=query))

        # Применение фильтра "Только продавцы онлайн"
        if filters["online_sellers"]:
            queryset = queryset.filter(seller__is_online=True)

        # Применение фильтра "Автоматическая доставка"
        if filters["auto_delivery"]:
            queryset = queryset.filter(is_auto_delivery=True)

        return queryset


class ChatMixin:
    def get_chat_messages(self):
        return ChatMessage.objects.filter(room_name="global_chat").order_by("timestamp")

    def get_context_data(self, **kwargs):
        # Получаем сообщения и добавляем их в контекст
        context = super().get_context_data(**kwargs)
        context["messages"] = self.get_chat_messages()
        return context


class ServiceChatMixin:
    def get_service_chat_messages(self, service=None):
        if service is None:
            service = self.get_object()  # Автоматически получаем объект, если не передан
        return ChatMessage.objects.filter(
            chat_room__object_id=service.id, chat_room__content_type=ContentType.objects.get_for_model(service)
        ).order_by("timestamp")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["messages"] = self.get_service_chat_messages()  # Теперь `service` передается автоматически
        return context
