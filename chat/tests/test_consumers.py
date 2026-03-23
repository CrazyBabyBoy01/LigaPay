import json

from asgiref.sync import sync_to_async
from channels.auth import AuthMiddlewareStack
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TestCase, TransactionTestCase

from chat.consumers import ChatConsumer
from chat.models import ChatMessage, ChatRoom
from chat.routing import websocket_urlpatterns
from LigaPay.asgi import application
from products.models import AccountService, Category


User = get_user_model()


class ChatConsumerUnitTests(TestCase):
    """Юнит-тесты для приватных методов ChatConsumer."""

    def setUp(self):
        """Создаёт пользователей и чаты для тестов."""
        self.buyer = User.objects.create_user(
            username='buyer', email='test1@example.com', password='12345'
        )
        self.seller = User.objects.create_user(
            username='seller', email='test2@example.com', password='12345'
        )
        self.outsider = User.objects.create_user(
            username='outsider', email='test3@example.com', password='12345'
        )
        self.room_global = ChatRoom.objects.create(is_global=True)
        self.room = ChatRoom.objects.create(buyer=self.buyer, seller=self.seller)

    def test_ensure_participant(self):
        """
        Проверяет логику допуска участника в чат.
        """
        consumer = ChatConsumer()

        self.assertTrue(consumer._ensure_participant(self.buyer, self.room_global))
        self.assertTrue(consumer._ensure_participant(self.outsider, self.room_global))

        self.assertTrue(consumer._ensure_participant(self.buyer, self.room))
        self.assertTrue(consumer._ensure_participant(self.seller, self.room))

        self.assertFalse(consumer._ensure_participant(self.outsider, self.room))

    def test_get_or_create_global_chat(self):
        """
        Проверяет создание или возврат глобального чата.
        """
        consumer = ChatConsumer()
        consumer._get_or_create_global_chat()
        self.assertEqual(ChatRoom.objects.filter(is_global=True).count(), 1)
        self.room_global.delete()
        self.assertEqual(ChatRoom.objects.filter(is_global=True).count(), 0)
        consumer._get_or_create_global_chat()
        self.assertEqual(ChatRoom.objects.filter(is_global=True).count(), 1)


class GetOrCreateServiceChatTests(TestCase):
    """Тесты для метода _get_or_create_service_chat в ChatConsumer."""

    def setUp(self):
        """
        Создаёт пользователей, тестовый сервис и экземпляр ChatConsumer.
        """
        self.buyer = User.objects.create_user(
            username='buyer', email='test1@example.com', password='12345'
        )
        self.seller = User.objects.create_user(
            username='seller', email='test2@example.com', password='12345'
        )
        self.outsider = User.objects.create_user(
            username='outsider', email='test3@example.com', password='12345'
        )
        category = Category.objects.create(name='product5', slug='product_slug4')
        self.product = AccountService.objects.create(
            title='Rp', seller=self.seller, price=100, category=category, quantity=5
        )
        self.room = ChatRoom.objects.create(buyer=self.buyer, seller=self.seller)
        self.service_type = 'accounts'
        self.service_id = self.product.id
        self.consumer = ChatConsumer()

    def test_invalid_service_type_returns_none(self):
        """
        Проверяет, что метод возвращает None,
        если service_type не существует в service_type_map и модель не найдена.
        """
        result = self.consumer._get_or_create_service_chat(
            self.buyer, service_type='invalid_type', service_id='12'
        )
        self.assertIs(result, None)

    def test_nonexistent_service_id_returns_none(self):
        """
        Проверяет, что метод возвращает None,
        если service_type существует, но услуги с таким ID нет.
        """
        result = self.consumer._get_or_create_service_chat(
            self.buyer, service_type='accounts', service_id='12'
        )
        self.assertIs(result, None)

    def test_buyer_equals_seller_returns_none(self):
        """
        Проверяет, что метод возвращает None,
        если buyer и seller — один и тот же пользователь.
        """
        result = self.consumer._get_or_create_service_chat(
            self.seller, service_type='accounts', service_id=self.service_id
        )
        self.assertIs(result, None)

    def test_returns_existing_chat_if_found(self):
        """
        Проверяет, что метод возвращает уже существующий чат,
        если он есть между buyer и seller.
        """
        result = self.consumer._get_or_create_service_chat(
            self.buyer, service_type='accounts', service_id=self.service_id
        )
        self.assertIs(result.id, self.room.id)

    def test_creates_new_chat_if_not_exists(self):
        """
        Проверяет, что метод создаёт новый чат,
        если ранее buyer и seller не общались.
        """
        self.assertEqual(ChatRoom.objects.count(), 1)
        result = self.consumer._get_or_create_service_chat(
            self.outsider, service_type='accounts', service_id=self.service_id
        )
        self.assertEqual(ChatRoom.objects.count(), 2)
        self.assertEqual(result.buyer, self.outsider)
        self.assertEqual(result.seller, self.seller)


class ChatConsumerWebsocketTests(TransactionTestCase):
    def setUp(self):
        """Создаёт пользователя и готовит URL."""
        self.user = User.objects.create_user(
            username='user', email='test123@example.com', password='12345'
        )
        self.application = application
        self.buyer = User.objects.create_user(
            username='buyer', email='test1@example.com', password='12345'
        )
        self.seller = User.objects.create_user(
            username='seller', email='test2@example.com', password='12345'
        )

        category = Category.objects.create(name='product5', slug='product_slug4')
        self.product = AccountService.objects.create(
            title='Rp', seller=self.seller, price=100, category=category, quantity=5
        )
        self.service_type = 'accounts'
        self.service_id = self.product.id

    async def test_connect_global_chat(self):
        """
        Проверяет успешное подключение к глобальному чату.
        """
        application = AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        communicator = WebsocketCommunicator(application, '/ws/chat/global_chat/')
        communicator.scope['user'] = self.user
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        count = await sync_to_async(ChatRoom.objects.filter(is_global=True).count)()
        self.assertEqual(count, 1)
        await communicator.disconnect()

    async def test_receive_and_save_message(self):
        """
        Проверяет, что сообщение сохраняется и передаётся группе.
        """
        application = AuthMiddlewareStack(URLRouter(websocket_urlpatterns))

        communicator = WebsocketCommunicator(application, '/ws/chat/global_chat/')
        communicator.scope['user'] = self.buyer

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # отправляем сообщение
        await communicator.send_to(text_data=json.dumps({'message': 'hello'}))

        # получаем ответ WS
        response = await communicator.receive_from()
        parsed = json.loads(response)

        # проверяем запись в БД
        msg_count = await sync_to_async(ChatMessage.objects.count)()
        self.assertEqual(msg_count, 1)

        msg = await sync_to_async(ChatMessage.objects.first)()
        self.assertEqual(msg.message, 'hello')
        self.assertEqual(msg.sender_id, self.buyer.id)

        # проверяем структуру ответа
        self.assertEqual(parsed['message'], 'hello')
        self.assertEqual(parsed['sender'], self.buyer.username)
        self.assertIn('timestamp', parsed)

        await communicator.disconnect()
