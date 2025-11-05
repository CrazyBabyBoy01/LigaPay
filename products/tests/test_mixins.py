from unittest.mock import MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase

from chat.models import ChatMessage, ChatRoom
from products.mixins import ServiceChatMixin


User = get_user_model()


class DummyBaseView:
    def get_context_data(self, **kwargs):
        # возвращает базовый контекст, чтобы миксин мог его дополнить
        return {}


class DummyServiceView(ServiceChatMixin, DummyBaseView):
    """Без group_messages — для тестов анонимного пользователя."""


class DummyServiceWithGrouping(ServiceChatMixin, DummyBaseView):
    """С group_messages — для теста group_messages."""

    def group_messages(self, messages):
        return ['custom']


class ServiceChatMixinTestCase(TestCase):
    """
    Тесты для ServiceChatMixin.
    Проверяют корректность поиска/создания комнаты чата между покупателем и продавцом,
    обработку отсутствия комнаты, неаутентифицированного пользователя
    и использование group_messages, если он определён во вью.
    """

    def setUp(self):
        """
        Создаёт пользователей (buyer, seller),
        комнату чата и несколько сообщений с разными timestamp.
        """
        self.seller = User.objects.create_user(
            username='seller', email='test1@example.com', password='pass123'
        )
        self.buyer = User.objects.create_user(
            username='buyer', email='test2@example.com', password='pass123'
        )
        self.buyer_2 = User.objects.create_user(
            username='buyer_@', email='test3@example.com', password='pass123'
        )
        self.room = ChatRoom.objects.create(buyer=self.buyer, seller=self.seller)
        self.message_1 = ChatMessage.objects.create(
            chat_room=self.room, sender=self.seller, message='sadka'
        )
        self.message_2 = ChatMessage.objects.create(
            chat_room=self.room, sender=self.buyer, message='sadka;daz'
        )

    def test_get_chat_messages_returns_sorted_messages_for_existing_room(self):
        """
        Проверяет, что при наличии комнаты метод возвращает сообщения,
        отсортированные по timestamp (по возрастанию).
        """
        chat = ServiceChatMixin()
        messages = chat.get_chat_messages(self.buyer, self.seller)
        self.assertEqual(list(messages), [self.message_1, self.message_2])
        self.assertEqual(len(messages), 2)

    def test_get_chat_messages_returns_empty_if_room_not_found(self):
        """
        Проверяет, что если комната не найдена, метод возвращает пустой список.
        """
        chat = ServiceChatMixin()
        messages = chat.get_chat_messages(self.buyer_2, self.seller)
        self.assertFalse(messages)
        self.assertEqual(len(messages), 0)

    def test_get_context_data_returns_empty_for_anonymous_user(self):
        """
        Проверяет, что при неаутентифицированном пользователе
        context['grouped_messages'] и context['messages'] — пустые списки.
        """
        request = MagicMock()
        request.user.is_authenticated = False
        service = DummyServiceView()
        service.request = request
        context = service.get_context_data()
        self.assertEqual(context['grouped_messages'], [])
        self.assertEqual(context['messages'], [])

    def test_get_context_data_uses_group_messages_if_defined(self):
        """
        Проверяет, что если во вью определён метод group_messages,
        он вызывается и его результат помещается в context['grouped_messages'].
        """
        request = MagicMock()
        request.user.is_authenticated = True
        service = DummyServiceWithGrouping()
        service.request = request
        service.get_chat_messages = MagicMock(return_value=['msg1', 'msg2'])
        service.object = MagicMock(seller=self.seller)
        context = service.get_context_data()
        self.assertEqual(context['grouped_messages'], ['custom'])
