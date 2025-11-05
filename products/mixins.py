import logging

from django.db.models import Q

from chat.models import ChatMessage, ChatRoom

from .models import Category


logger = logging.getLogger(__name__)


class CategoryMixin:
    """
    Миксин для получения категории по slug и добавления ее в контекст.
    """

    background_image = '/static/deps/images/SB_Riven.jpg'

    def get_category(self, slug):
        try:
            return Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        slug = kwargs.get('slug', None)

        if slug:
            category = self.get_category(slug)
            context['category'] = category

        context['categories'] = Category.objects.all()

        return context


class PaginateMixin:
    paginate_by = 3


class ChatMixin:
    def get_chat_messages(self):
        global_room = ChatRoom.objects.get(is_global=True)
        return global_room.messages.order_by('timestamp')

    def get_context_data(self, **kwargs):
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
            messages = (
                ChatMessage.objects.filter(chat_room=room).select_related('sender').order_by('timestamp')
            )
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
