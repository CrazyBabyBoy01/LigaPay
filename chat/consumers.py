import json
import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.apps import apps
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q

from .models import ChatMessage, ChatRoom


logger = logging.getLogger(__name__)


class ChatConsumer(WebsocketConsumer):
    """WebSocket consumer для обработки чатов (глобальный и приватные)."""

    def _set_room_and_group(self, chat_room):
        """Установить активную комнату и имя группы по её id."""
        self.chat_room = chat_room
        self.room_group_name = f'chat_{chat_room.id}'

    def _get_or_create_global_chat(self):
        """Вернуть глобальную комнату (создать, если нет)."""
        chat_room, _ = ChatRoom.objects.get_or_create(is_global=True)
        return chat_room

    def _ensure_participant(self, user, chat_room) -> bool:
        """Проверить, что пользователь является участником чата или это глобальная комната."""
        return bool(chat_room.is_global or user == chat_room.buyer or user == chat_room.seller)

    def _broadcast_message(self, message, user, chat_message):
        """Отправить событие в группу текущей комнаты."""
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': user.username,
                'timestamp': chat_message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            },
        )

    def _get_or_create_service_chat(self, buyer, service_type, service_id):
        """Получить или создать приватный чат между buyer и seller по услуге."""

        service_type_map = {
            'riot-points': 'rpservice',
            'battle-pass': 'battlepassservice',
            'boosting': 'boostservice',
            'qualification': 'qualificationservice',
            'other': 'otherservice',
            'services': 'generalservice',
            'donation': 'donationservice',
            'training': 'trainingservice',
            'accounts': 'accountservice',
        }
        service_type = service_type_map.get(service_type, service_type)
        try:
            service_model = apps.get_model('products', service_type)
        except LookupError:
            return None

        try:
            service = service_model.objects.get(id=service_id)
            seller = service.seller
        except service_model.DoesNotExist:
            return None
        if buyer == seller:
            return None
        chat_room = ChatRoom.objects.filter(
            Q(buyer=buyer, seller=seller) | Q(buyer=seller, seller=buyer)
        ).first()
        if chat_room:
            return chat_room
        return ChatRoom.objects.create(buyer=buyer, seller=seller)

    def connect(self):
        """Обработчик подключения к WebSocket.

        Определяет тип чата (по id, глобальный или сервисный),
        проверяет права пользователя и подключает к группе.
        """
        route_kwargs = self.scope['url_route']['kwargs']
        chat_id = route_kwargs.get('chat_id')
        service_type = route_kwargs.get('service_type')
        service_id = route_kwargs.get('service_id')
        user = self.scope['user']
        logger.info(
            f'Подключение к WebSocket: chat_id={chat_id}, '
            f'service_type={service_type}, service_id={service_id}'
        )

        if chat_id:
            try:
                self.chat_room = ChatRoom.objects.get(id=chat_id)
                if not self._ensure_participant(user, self.chat_room):
                    logger.warning(
                        'Пользователь %s не является участником комнаты %s',
                        user,
                        self.chat_room,
                    )
                    self.close()
                    return
                self._set_room_and_group(self.chat_room)
            except ChatRoom.DoesNotExist:
                logger.error(f'Чат с id={chat_id} не найден')
                self.close()
                return

        elif service_type == 'global_chat' or (service_type is None and service_id is None):
            self.chat_room = self._get_or_create_global_chat()
            self._set_room_and_group(self.chat_room)

        elif service_type and service_id:
            buyer = self.scope['user']

            if buyer.is_anonymous:
                self.close()
                return
            chat_room = self._get_or_create_service_chat(buyer, service_type, service_id)
            if not chat_room:
                logger.error(f'Не удалось создать/получить чат для service_id={service_id}')
                self.close()
                return
            if not self._ensure_participant(user, chat_room):
                logger.warning(f'Пользователь {user} не является участником комнаты {self.chat_room}')
                self.close()
                return
            self._set_room_and_group(chat_room)
        else:
            logger.error('Ошибка: `room_group_name` не определен!')
            self.close()
            return

        logger.info(f'Подключение: user={user.username}, room={self.chat_room}')
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        """Обработчик отключения от WebSocket.

        Убирает текущее соединение из группы и пишет лог.
        """
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)
        logger.info(f"Отключение: user={self.scope['user'].username}, room={self.chat_room}")

    def receive(self, text_data):
        """Обработчик входящих сообщений от клиента.

        Проверяет авторизацию, сохраняет сообщение в базе
        и транслирует его всем участникам комнаты.
        """
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')
        user = self.scope.get('user', AnonymousUser())

        if user.is_anonymous:
            self.send(text_data=json.dumps({'error': 'Вы не авторизованы!'}))
            logger.warning('Попытка отправить сообщение от анонимного пользователя')
            return

        logger.info(f'Получено сообщение от {user.username}: {message}')

        try:
            chat_message = ChatMessage.objects.create(
                chat_room=self.chat_room, sender=user, message=message
            )
            logger.info(f'Сообщение сохранено в комнате {self.chat_room}')
            logger.info(f'Отправка сообщения в группу: {self.room_group_name}')
            self._broadcast_message(message, user, chat_message)

        except Exception as e:
            logger.error(f'Ошибка при сохранении сообщения: {e}')

    def chat_message(self, event):
        """Обработчик события для рассылки сообщений в WebSocket."""
        self.send(text_data=json.dumps(event))

    def order_created(self, event):
        """Обработчик события 'order_created'.

        Отправляет в WebSocket информацию о создании заказа.
        """
        logger.info(f"order_created: order_id={event['order_id']}")
        self.send(
            text_data=json.dumps(
                {
                    'type': 'order_created',
                    'order_id': event['order_id'],
                    'csrf_token': event['csrf_token'],
                    'buyer_username': event.get('buyer_username'),
                    'seller_username': event.get('seller_username'),
                }
            )
        )

    def order_confirmed(self, event):
        """Обработчик события 'order_confirmed'.

        Отправляет в WebSocket информацию о подтверждении заказа.
        """
        logger.info(f"order_confirmed: order_id={event['order_id']}")
        self.send(
            text_data=json.dumps(
                {
                    'type': 'order_confirmed',
                    'order_id': event['order_id'],
                    'message': event['message'],
                }
            )
        )
