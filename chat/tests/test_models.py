from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from chat.models import ChatMessage, ChatRoom


User = get_user_model()


class ChatRoomManagerTests(TestCase):
    """Тесты для методов менеджера ChatRoomManager."""

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

    def test_for_user_returns_only_related_chats(self):
        """
        Проверяет, что метод for_user возвращает только чаты,
        где пользователь является покупателем или продавцом.
        """
        result = ChatRoom.objects.for_user(self.buyer)
        self.assertIn(self.room, ChatRoom.objects.for_user(self.buyer))
        self.assertIn(self.room, ChatRoom.objects.for_user(self.seller))
        self.assertNotIn(self.room, ChatRoom.objects.for_user(self.outsider))
        self.assertEqual(result.count(), 1)
        self.assertNotIn(self.room_global, result)


class ChatRoomQuerySetTests(TestCase):
    """Тесты для методов QuerySet в ChatRoomQuerySet."""

    def setUp(self):
        """Создаёт пользователей, чаты и сообщения."""
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

        now = timezone.now()
        ChatMessage.objects.filter(pk=self.message_1.pk).update(timestamp=now)
        ChatMessage.objects.filter(pk=self.message_2.pk).update(timestamp=now + timedelta(seconds=10))
        ChatMessage.objects.filter(pk=self.message_3.pk).update(timestamp=now + timedelta(seconds=20))
        ChatMessage.objects.filter(pk=self.message_4.pk).update(timestamp=now + timedelta(seconds=30))

    def test_last_messages_returns_correct_annotations(self):
        """
        Проверяет, что метод last_messages() добавляет корректные
        поля last_message_text и last_message_time, соответствующие
        последнему сообщению.
        """
        rooms = list(ChatRoom.objects.all().last_messages())
        self.assertEqual(rooms[0], self.room_2)
        self.assertEqual(rooms[0].last_message_text, self.message_4.message)
        self.assertEqual(rooms[1], self.room_1)
        self.assertEqual(rooms[1].last_message_text, self.message_2.message)

    def test_with_unread_counts_returns_correct_numbers(self):
        """
        Проверяет, что метод with_unread_counts(user) корректно считает
        количество непрочитанных сообщений, исключая те, что отправлены самим пользователем.
        """
        self.message_1.is_read = True
        self.message_1.save()

        buyer_rooms = ChatRoom.objects.all().with_unread_counts(self.buyer)
        room1_buyer = next(r for r in buyer_rooms if r.id == self.room_1.id)
        self.assertEqual(room1_buyer.unread_count, 0)

        seller_rooms = ChatRoom.objects.all().with_unread_counts(self.seller)
        room1_seller = next(r for r in seller_rooms if r.id == self.room_1.id)
        self.assertEqual(room1_seller.unread_count, 1)
