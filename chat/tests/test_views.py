from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from chat.models import ChatMessage, ChatRoom


User = get_user_model()


class UnreadMessageCountAPITests(TestCase):
    """Тесты для API-эндпоинта unread_message_count_api."""

    def setUp(self):
        """Создаёт пользователя и клиент с авторизацией."""
        self.user = User.objects.create_user(
            username='newuser1', email='test1@example.com', password='pass123'
        )
        self.seller = User.objects.create_user(
            username='newuser12', email='test12@example.com', password='pass123'
        )
        self.client.force_login(self.user)
        self.room = ChatRoom.objects.create(buyer=self.user, seller=self.seller)

    def test_returns_correct_unread_count(self):
        """
        Проверяет, что API возвращает корректное количество непрочитанных сообщений
        для авторизованного пользователя.
        """

        ChatMessage.objects.create(chat_room=self.room, sender=self.seller, message='1', is_read=False)
        url = reverse('chat:unread_message_count_api')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'unread_count': 1})


class ChatRoomViewTests(TestCase):
    """Тесты для ChatRoomView (глобальный чат)."""

    def setUp(self):
        """Создаёт клиента и URL."""
        self.user = User.objects.create_user(
            username='newuser1', email='test1@example.com', password='pass123'
        )
        self.client.force_login(self.user)
        self.url = reverse('chat:chat_room')

    def test_creates_global_chat_if_not_exists(self):
        """
        Проверяет, что при первом запросе создаётся глобальный чат,
        а при повторном — не создаются дубликаты.
        """
        self.assertEqual(ChatRoom.objects.filter(is_global=True).count(), 0)
        self.client.get(self.url)
        self.assertEqual(ChatRoom.objects.filter(is_global=True).count(), 1)
        self.client.get(self.url)
        self.assertEqual(ChatRoom.objects.filter(is_global=True).count(), 1)


class DialogsViewTests(TestCase):
    """Тесты для DialogsView — списка чатов пользователя."""

    def setUp(self):
        """Создаёт пользователей и чаты."""
        self.buyer = User.objects.create_user(
            username='buyer', email='test1@example.com', password='12345'
        )
        self.seller = User.objects.create_user(
            username='seller', email='test2@example.com', password='12345'
        )
        self.outsider = User.objects.create_user(
            username='outsider', email='test3@example.com', password='12345'
        )
        self.room_1 = ChatRoom.objects.create(buyer=self.buyer, seller=self.seller)
        self.room_2 = ChatRoom.objects.create(buyer=self.buyer, seller=self.outsider)
        self.room_3 = ChatRoom.objects.create(buyer=self.outsider, seller=self.seller)
        self.client.force_login(self.buyer)
        self.url = reverse('chat:chat_dialogs')

    def test_returns_only_user_related_chats(self):
        """
        Проверяет, что DialogsView отображает только чаты,
        в которых участвует авторизованный пользователь.
        """
        self.client.get(self.url)
        response = self.client.get(self.url)
        chat_rooms = response.context['chat_rooms']
        chat_rooms = list(response.context['chat_rooms'])
        self.assertIn(self.room_1, chat_rooms)
        self.assertIn(self.room_2, chat_rooms)
        self.assertNotIn(self.room_3, chat_rooms)


class DialogDetailViewTests(TestCase):
    """Тесты для DialogDetailView — конкретного диалога."""

    def setUp(self):
        """Создаёт пользователей, чат и сообщения."""
        self.buyer = User.objects.create_user(
            username='buyer', email='test1@example.com', password='12345'
        )
        self.seller = User.objects.create_user(
            username='seller', email='test2@example.com', password='12345'
        )
        self.outsider = User.objects.create_user(
            username='outsider', email='test3@example.com', password='12345'
        )
        self.room_1 = ChatRoom.objects.create(buyer=self.buyer, seller=self.seller)
        self.room_2 = ChatRoom.objects.create(buyer=self.buyer, seller=self.outsider)
        self.message_1 = ChatMessage.objects.create(
            chat_room=self.room_1, sender=self.seller, message='1'
        )
        self.message_2 = ChatMessage.objects.create(
            chat_room=self.room_1, sender=self.buyer, message='2'
        )
        self.message_3 = ChatMessage.objects.create(
            chat_room=self.room_2, sender=self.seller, message='3'
        )
        self.message_4 = ChatMessage.objects.create(
            chat_room=self.room_2, sender=self.buyer, message='4'
        )
        self.url = reverse('chat:chat_dialog_detail', kwargs={'chat_id': self.room_1.id})
        now = timezone.now()
        ChatMessage.objects.filter(pk=self.message_1.pk).update(timestamp=now)
        ChatMessage.objects.filter(pk=self.message_2.pk).update(timestamp=now + timedelta(seconds=10))
        ChatMessage.objects.filter(pk=self.message_3.pk).update(timestamp=now + timedelta(seconds=20))
        ChatMessage.objects.filter(pk=self.message_4.pk).update(timestamp=now + timedelta(seconds=30))

    def test_access_denied_for_unauthorized_user(self):
        """
        Проверяет, что посторонний пользователь не может открыть диалог.
        """
        self.client.force_login(self.outsider)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_marks_messages_as_read_for_authorized_user(self):
        """
        Проверяет, что непрочитанные сообщения помечаются как прочитанные,
        когда участник открывает чат.
        """
        self.client.force_login(self.buyer)
        self.assertFalse(self.message_1.is_read)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.message_1.refresh_from_db()
        self.assertTrue(self.message_1.is_read)
        self.message_2.refresh_from_db()
        self.assertFalse(self.message_2.is_read)
