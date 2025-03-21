import json
import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from django.utils.timezone import now

from .models import ChatMessage


logger = logging.getLogger(__name__)  # Логгер для отладки


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        # Получаем имя комнаты из URL (если ты поменяешь routing, будет подставляться нужная комната)
        self.room_name = self.scope["url_route"]["kwargs"].get("room_name", "global_chat")
        self.room_group_name = f"chat_{self.room_name}"

        # Присоединяемся к группе WebSocket
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)

        self.accept()

    def disconnect(self, close_code):
        # Отключение от группы WebSocket
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get("message", "")

        # Получаем пользователя (если он анонимный, можно обработать иначе)
        user = self.scope.get("user", AnonymousUser())
        # Логируем пользователя
        logger.info(f"Отправитель: {user} (username: {getattr(user, 'username', 'None')})")
        if user.is_anonymous:
            self.send(text_data=json.dumps({"error": "Вы не авторизованы!"}))
            return
        # 🚀 Логируем полученное сообщение
        logger.info(f"Получено сообщение от {user.username}: {message}")
        # Сохраняем сообщение в базу данных
        try:
            # Сохраняем сообщение в базе
            chat_message = ChatMessage.objects.create(
                room_name=self.room_name, sender=user, message=message, timestamp=now()
            )
            logger.info(f"Сообщение сохранено в БД: {chat_message}")

            # Отправляем сообщение всем в группе
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender": user.username,
                    "timestamp": chat_message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                },
            )
        except Exception as e:
            logger.error(f"Ошибка при сохранении сообщения: {e}")

    def chat_message(self, event):
        # Отправляем сообщение всем подключенным клиентам
        self.send(text_data=json.dumps(event))
