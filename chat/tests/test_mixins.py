from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from chat.mixin import GroupedMessagesMixin
from chat.models import ChatMessage, ChatRoom
from users.models import User


class GroupedMessagesMixinTests(TestCase):
    """Тесты для метода group_messages() из GroupedMessagesMixin."""

    def setUp(self):
        """
        Создаёт пользователей, комнату и экземпляр миксина.
        """
        self.mixin = GroupedMessagesMixin()

        self.user1 = User.objects.create_user(username='user1', email='u1@example.com', password='pass')
        self.user2 = User.objects.create_user(username='user2', email='u2@example.com', password='pass')

        self.room = ChatRoom.objects.create(buyer=self.user1, seller=self.user2)

        self.t = timezone.now()

    def test_groups_messages_from_same_sender_within_one_minute(self):
        """
        Проверяет, что сообщения одного и того же отправителя,
        отправленные в пределах 1 минуты, объединяются в одну группу.
        """
        msg1 = ChatMessage.objects.create(
            chat_room=self.room, sender=self.user1, message='m1', timestamp=self.t
        )

        msg2 = ChatMessage.objects.create(
            chat_room=self.room,
            sender=self.user1,
            message='m2',
            timestamp=(self.t + timedelta(seconds=30)),
        )

        msg3 = ChatMessage.objects.create(
            chat_room=self.room,
            sender=self.user1,
            message='m3',
            timestamp=(self.t + timedelta(seconds=59)),
        )
        messages = [msg1, msg2, msg3]
        result = self.mixin.group_messages(messages)
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]['messages']), 3)
        self.assertEqual(result[0]['sender'], self.user1)
        self.assertEqual(result[0]['messages'], ['m1', 'm2', 'm3'])

    def test_splits_groups_when_sender_changes(self):
        """
        Проверяет, что сообщения от разных отправителей попадают
        в разные группы, даже если время отличается менее чем на минуту.
        """
        msg1 = ChatMessage.objects.create(
            chat_room=self.room, sender=self.user1, message='m1', timestamp=self.t
        )

        msg2 = ChatMessage.objects.create(
            chat_room=self.room,
            sender=self.user2,
            message='m2',
            timestamp=self.t,
        )

        msg3 = ChatMessage.objects.create(
            chat_room=self.room,
            sender=self.user1,
            message='m3',
            timestamp=self.t,
        )
        messages = [msg1, msg2, msg3]
        result = self.mixin.group_messages(messages)
        self.assertEqual(len(result), 3)
        self.assertEqual(len(result[0]['messages']), 1)
        self.assertEqual(result[0]['sender'], self.user1)
        self.assertEqual(result[1]['sender'], self.user2)

    def test_splits_groups_when_time_exceeded(self):
        """
        Проверяет, что если между сообщениями одного отправителя прошло
        больше 1 минуты, они создают отдельные группы.
        """
        msg1 = ChatMessage.objects.create(chat_room=self.room, sender=self.user1, message='m1')

        msg2 = ChatMessage.objects.create(
            chat_room=self.room,
            sender=self.user1,
            message='m2',
        )
        ChatMessage.objects.filter(pk=msg2.pk).update(timestamp=self.t + timedelta(minutes=2))
        msg2.refresh_from_db()
        messages = [msg1, msg2]
        result = self.mixin.group_messages(messages)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['sender'], self.user1)
        self.assertEqual(result[1]['sender'], self.user1)

    def test_empty_list_returns_empty(self):
        """
        Проверяет, что при передаче пустого списка сообщений
        метод возвращает пустой список.
        """
        messages = []
        result = self.mixin.group_messages(messages)
        self.assertEqual(len(result), 0)

