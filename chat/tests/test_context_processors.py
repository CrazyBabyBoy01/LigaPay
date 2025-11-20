from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from chat.context_processors import unread_message_count
from chat.models import ChatMessage, ChatRoom
from users.models import User


class UnreadMessageCountContextProcessorTests(TestCase):
    """Тесты для контекстного процессора unread_message_count."""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='user1', email='test@example.com', password='12345'
        )

    def test_returns_zero_for_anonymous_user(self):
        """
        Проверяет, что анонимный пользователь всегда получает 0.
        """
        request = self.factory.get('/')
        request.user = AnonymousUser()

        result = unread_message_count(request)

        self.assertEqual(result, {'unread_message_count': 0})

    def test_returns_actual_count_for_authenticated_user(self):
        """
        Проверяет, что для авторизованного пользователя
        возвращается правильное количество непрочитанных сообщений,
        отправленных ДРУГИМИ пользователями.
        """
        request = self.factory.get('/')
        request.user = self.user

        other = User.objects.create_user(username='other', email='other@example.com', password='pass')

        room = ChatRoom.objects.create(buyer=self.user, seller=other)

        ChatMessage.objects.create(chat_room=room, sender=other, message='1', is_read=False)
        ChatMessage.objects.create(chat_room=room, sender=other, message='2', is_read=False)
        ChatMessage.objects.create(chat_room=room, sender=other, message='3', is_read=False)

        result = unread_message_count(request)

        self.assertEqual(result['unread_message_count'], 3)
