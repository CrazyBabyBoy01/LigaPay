import logging

from django.db.models import Q

from chat.models import ChatMessage, ChatRoom

from .models import Category


logger = logging.getLogger(__name__)


class ExcludeOwnServicesMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Проверяем, анонимный ли пользователь
        if user.is_authenticated:
            logger.debug('🔍 Пользователь анонимный — возвращаем все карточки')
            return queryset

        before_count = queryset.count()
        # Фильтруем по исключению собственных услуг
        filtered_qs = queryset.exclude(seller=user)
        after_count = filtered_qs.count()

        # Логируем до и после фильтрации
        logger.debug(
            f'🔍 Фильтрация карточек: было {before_count}, после фильтрации своих — {after_count}'
        )
        return filtered_qs


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
        slug = kwargs.get('slug', None)

        if slug:
            category = self.get_category(slug)  # Получаем категорию по переданному слагу
            context['category'] = category

        # Получаем все категории для списка
        context['categories'] = Category.objects.all()

        return context


class PaginateMixin:
    paginate_by = 3


class SearchDescriptionMixin:
    """
    Миксин для обработки поиска и фильтров по полям `title`,
    `search_description`, а также других фильтров.
    """

    def get_search_query(self):
        """
        Возвращает строку запроса для поиска по полям `title` и `search_description`.
        """
        query = self.request.GET.get('q', '')
        return query.strip()

    def get_filters(self):
        """
        Возвращает фильтры из запроса.
        """
        return {
            'online_sellers': self.request.GET.get('online_sellers') == 'on',
            'auto_delivery': self.request.GET.get('auto_delivery') == 'on',
        }

    def get_queryset(self):
        """
        Фильтрует объекты модели на основе запроса по полям `title`,
        `search_description` и дополнительных фильтров.
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
        if filters['online_sellers']:
            queryset = queryset.filter(seller__is_online=True)

        # Применение фильтра "Автоматическая доставка"
        if filters['auto_delivery']:
            queryset = queryset.filter(is_auto_delivery=True)
        return queryset


class ChatMixin:
    def get_chat_messages(self):
        return ChatMessage.objects.filter(room_name='global_chat').order_by('timestamp')

    def get_context_data(self, **kwargs):
        # Получаем сообщения и добавляем их в контекст
        context = super().get_context_data(**kwargs)
        context['messages'] = self.get_chat_messages()
        return context


class ServiceChatMixin:
    def get_chat_messages(self, buyer, seller):
        room = ChatRoom.objects.filter(
            Q(buyer=buyer, seller=seller) | Q(buyer=seller, seller=buyer)
        ).first()

        if room:
            logger.info(f'Комната найдена: {room}')
            messages = ChatMessage.objects.filter(chat_room=room).order_by('timestamp')
        else:
            logger.warning(f'Чат между {buyer} и {seller} не найден.')
            messages = []

        return messages

    def get_context_data(self, **kwargs):
        logger.info('Получаем контекст для чата между покупателем и продавцом.')

        context = super().get_context_data(**kwargs)

        service = getattr(self, 'object', None)
        buyer = self.request.user

        if buyer.is_authenticated and service:
            seller = getattr(service, 'seller', None)

            if seller:
                messages = self.get_chat_messages(buyer, seller)

                # 👉 группируем сообщения, если есть миксин
                if hasattr(self, 'group_messages'):
                    context['grouped_messages'] = self.group_messages(messages)
                else:
                    context['grouped_messages'] = messages
            else:
                logger.warning('Продавец не найден.')
                context['messages'] = []
        else:
            logger.warning('Пользователь не аутентифицирован или объект услуги не найден.')
            context['grouped_messages'] = []
            context['messages'] = []

        logger.info(f"Контекст содержит {len(context['grouped_messages'])} сообщений.")
        return context
