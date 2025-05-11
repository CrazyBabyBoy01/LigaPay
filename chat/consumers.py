import json
import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now

from .models import ChatMessage, ChatRoom


logger = logging.getLogger(__name__)  # Логгер для отладки


# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#         # Получаем имя комнаты из URL (если ты поменяешь routing, будет подставляться нужная комната)
#         self.room_name = self.scope["url_route"]["kwargs"].get("room_name", "global_chat")
#         self.room_group_name = f"chat_{self.room_name}"

#         # Присоединяемся к группе WebSocket
#         async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)

#         self.accept()

#     def disconnect(self, close_code):
#         # Отключение от группы WebSocket
#         async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

#     def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json.get("message", "")

#         # Получаем пользователя (если он анонимный, можно обработать иначе)
#         user = self.scope.get("user", AnonymousUser())
#         # Логируем пользователя
#         logger.info(f"Отправитель: {user} (username: {getattr(user, 'username', 'None')})")
#         if user.is_anonymous:
#             self.send(text_data=json.dumps({"error": "Вы не авторизованы!"}))
#             return
#         # 🚀 Логируем полученное сообщение
#         logger.info(f"Получено сообщение от {user.username}: {message}")
#         # Сохраняем сообщение в базу данных
#         try:
#             # Сохраняем сообщение в базе
#             chat_message = ChatMessage.objects.create(
#                 room_name=self.room_name, sender=user, message=message, timestamp=now()
#             )
#             logger.info(f"Сообщение сохранено в БД: {chat_message}")

#             # Отправляем сообщение всем в группе
#             async_to_sync(self.channel_layer.group_send)(
#                 self.room_group_name,
#                 {
#                     "type": "chat_message",
#                     "message": message,
#                     "sender": user.username,
#                     "timestamp": chat_message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
#                 },
#             )
#         except Exception as e:
#             logger.error(f"Ошибка при сохранении сообщения: {e}")

#     def chat_message(self, event):
#         # Отправляем сообщение всем подключенным клиентам
#         self.send(text_data=json.dumps(event))


# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#         # Получаем параметры из URL
#         service_type = self.scope["url_route"]["kwargs"].get("service_type")
#         service_id = self.scope["url_route"]["kwargs"].get("service_id")

#         logger.info(f"🔄 Подключение к WebSocket: service_type={service_type}, service_id={service_id}")

#         if service_type == "global_chat" or (service_type is None and service_id is None):
#             # 🟢 Общий чат
#             self.room_name = "global_chat"
#             self.room_group_name = "chat_global_chat"

#         elif service_type and service_id:
#             #  2️⃣ 🛒 Если это чат по услуге
#             service_type = self.scope["url_route"]["kwargs"].get("service_type")
#             service_id = self.scope["url_route"]["kwargs"].get("service_id")
#             buyer = self.scope["user"]

#             if buyer.is_anonymous:
#                 self.close()
#                 return

#             # 🔹 **Маппинг названий моделей**
#             service_type_map = {
#                 "riot-points": "rpservice",
#                 "battlepass": "battlepassservice",
#                 "boost": "boostservice",
#                 # Добавь другие сервисы, если нужно
#             }
#             service_type = service_type_map.get(service_type, service_type)  # Приводим к нужному имени
#             # Определяем услугу и продавца
#             try:
#                 service_model = ContentType.objects.get(model=service_type).model_class()
#                 service = service_model.objects.get(id=service_id)
#                 seller = service.seller  # Убедись, что у услуги есть поле seller
#             except Exception as e:
#                 logger.error(f"❌ Ошибка поиска услуги: {e}")
#                 self.close()
#                 return

#             # Создаем или получаем чат-комнату
#             self.chat_room, created = ChatRoom.objects.get_or_create(
#                 content_type=ContentType.objects.get_for_model(service),
#                 object_id=service.id,
#                 buyer=buyer,
#                 seller=seller,
#             )
#             self.room_group_name = f"chat_{self.chat_room.id}"

#         else:
#             logger.error("❌ Ошибка: `room_group_name` не определен!")
#             self.close()
#             return

#         logger.info(f"✅ Подключаемся к комнате: {self.room_group_name}")

#         # Подключаемся к группе
#         async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
#         self.accept()

#     def disconnect(self, close_code):
#         # Отключение от группы WebSocket
#         # async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)
#         if hasattr(self, "room_group_name") and self.room_group_name:
#             async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

#     def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json.get("message", "")

#         user = self.scope.get("user", AnonymousUser())
#         if user.is_anonymous:
#             self.send(text_data=json.dumps({"error": "Вы не авторизованы!"}))
#             return

#         logger.info(f"Получено сообщение от {user.username}: {message}")

#         try:
#             if hasattr(self, "room_name") and self.room_name == "global_chat":
#                 # ✅ Сохраняем `global_chat` без `ChatRoom`
#                 chat_message = ChatMessage.objects.create(
#                     room_name="global_chat", sender=user, message=message, timestamp=now()
#                 )
#                 logger.info("💬 Сообщение сохранено в ОБЩЕМ ЧАТЕ")
#             else:
#                 # ✅ Чат по услуге, сохраняем с `ChatRoom`
#                 chat_message = ChatMessage.objects.create(
#                     chat_room=self.chat_room, sender=user, message=message, timestamp=now()
#                 )
#                 logger.info(f"💬 Сообщение сохранено в чате услуги (ID {self.chat_room.id})")
#             logger.info(f"Сообщение сохранено в БД: {chat_message}")

#             # Отправляем сообщение всем в группе
#             async_to_sync(self.channel_layer.group_send)(
#                 self.room_group_name,
#                 {
#                     "type": "chat_message",
#                     "message": message,
#                     "sender": user.username,
#                     "timestamp": chat_message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
#                 },
#             )
#             logger.info(f"Сообщение сохранено в БД: {chat_message}")
#         except Exception as e:
#             logger.error(f"Ошибка при сохранении сообщения: {e}")

#     def chat_message(self, event):
#         # Отправляем сообщение всем подключенным клиентам
#         self.send(text_data=json.dumps(event))


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        # Получаем параметры из URL
        service_type = self.scope["url_route"]["kwargs"].get("service_type")
        service_id = self.scope["url_route"]["kwargs"].get("service_id")

        logger.info(f"🔄 Подключение к WebSocket: service_type={service_type}, service_id={service_id}")

        if service_type == "global_chat" or (service_type is None and service_id is None):
            # 🟢 Общий чат
            self.room_name = "global_chat"
            self.room_group_name = "chat_global_chat"

        elif service_type and service_id:
            # 🛒 Чат по услуге
            buyer = self.scope["user"]

            if buyer.is_anonymous:
                self.close()
                return

            service_type_map = {
                "riot-points": "rpservice",
                "battle-pass": "battlepassservice",
                "boosting": "boostservice",
                "qualification": "qualificationservice",
                "other": "otherservice",
                "services": "generalservice",
                "donation": "donationservice",
                "training": "trainingservice",
                "accounts": "accountservice",
            }
            service_type = service_type_map.get(service_type, service_type)

            try:
                service_model = ContentType.objects.get(model=service_type).model_class()
                service = service_model.objects.get(id=service_id)
                seller = service.seller  # Убедись, что у услуги есть поле seller
            except Exception as e:
                logger.error(f"❌ Ошибка поиска услуги: {e}")
                self.close()
                return

            # Создаем или получаем чат-комнату
            self.chat_room, created = ChatRoom.objects.get_or_create(
                content_type=ContentType.objects.get_for_model(service),
                object_id=service.id,
                buyer=buyer,
                seller=seller,
            )
            self.room_name = f"service_chat_{service_id}"  # Добавляем уникальное имя для услуги
            self.room_group_name = f"chat_{self.chat_room.id}"
        else:
            logger.error("❌ Ошибка: `room_group_name` не определен!")
            self.close()
            return

        logger.info(f"✅ Подключаемся к комнате: {self.room_group_name}")
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        if hasattr(self, "room_group_name") and self.room_group_name:
            async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get("message", "")
        user = self.scope.get("user", AnonymousUser())

        if user.is_anonymous:
            self.send(text_data=json.dumps({"error": "Вы не авторизованы!"}))
            return

        logger.info(f"Получено сообщение от {user.username}: {message}")

        try:
            if self.room_name == "global_chat":
                chat_message = ChatMessage.objects.create(
                    room_name="global_chat", sender=user, message=message, timestamp=now()
                )
                logger.info("💬 Сообщение сохранено в ОБЩЕМ ЧАТЕ")
            elif hasattr(self, "chat_room"):
                chat_message = ChatMessage.objects.create(
                    chat_room=self.chat_room, sender=user, message=message, timestamp=now()
                )
                logger.info(f"💬 Сообщение сохранено в чате услуги (ID {self.chat_room.id})")
            else:
                logger.error("❌ Ошибка: `chat_room` не найден для чата услуги!")
                return
            logger.info(f"📤 Отправка сообщения в группу: {self.room_group_name}")
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
        self.send(text_data=json.dumps(event))

    def order_created(self, event):
        logger.info(f"📨 Получено событие order_created: {event}")
        self.send(
            text_data=json.dumps(
                {
                    "type": "order_created",
                    "order_id": event["order_id"],
                    "csrf_token": event["csrf_token"],
                }
            )
        )

    def order_confirmed(self, event):
        logger.info(f"📨 Получено событие order_confirmed: {event}")
        self.send(
            text_data=json.dumps(
                {
                    "type": "order_confirmed",
                    "order_id": event["order_id"],
                    "message": event["message"],
                }
            )
        )
