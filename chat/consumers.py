import json
import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.apps import apps
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now
from django.db.models import Q
from .models import ChatMessage, ChatRoom


logger = logging.getLogger(__name__)  # Логгер для отладки


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        # Получаем параметры из URL
        route_kwargs = self.scope["url_route"]["kwargs"]
        chat_id = route_kwargs.get("chat_id")
        service_type = route_kwargs.get("service_type")
        service_id = route_kwargs.get("service_id")

        logger.info(
            f"🔄 Подключение к WebSocket: chat_id={chat_id}, service_type={service_type}, service_id={service_id}"
        )
        user = self.scope["user"]
        if chat_id:
            try:
                self.chat_room = ChatRoom.objects.get(id=chat_id)
                self.buyer = self.chat_room.buyer
                self.seller = self.chat_room.seller

                # Проверка, что текущий пользователь — участник
                if user != self.buyer and user != self.seller:
                    logger.warning("❌ Пользователь не является участником чата")
                    self.close()
                    return

                self.room_name = f"private_chat_{chat_id}"
                self.room_group_name = f"chat_{chat_id}"
            except ChatRoom.DoesNotExist:
                logger.error(f"❌ Чат с ID {chat_id} не найден!")
                self.close()
                return

        elif service_type == "global_chat" or (service_type is None and service_id is None):
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
                service_model = apps.get_model("products", service_type)
                service = service_model.objects.get(id=service_id)
                seller = service.seller  # Убедись, что у услуги есть поле seller
            except Exception as e:
                logger.error(f"❌ Ошибка поиска услуги: {e}")
                self.close()
                return
            logger.info(f"🧾 Попытка создать или получить чат: buyer={buyer.username}, seller={seller.username}")



            chat_room = ChatRoom.objects.filter(
                        Q(buyer=buyer, seller=seller) | Q(buyer=seller, seller=buyer)
                    ).first()

            if chat_room:
                self.chat_room = chat_room
            else:
                self.chat_room = ChatRoom.objects.create(buyer=buyer, seller=seller)




            # # Упорядочиваем пользователей по id
            # user1, user2 = sorted([buyer, seller], key=lambda u: u.id)

            # # Создаем или получаем чат-комнату независимо от ролей
            # self.chat_room, created = ChatRoom.objects.get_or_create(
            #     buyer=user1,
            #     seller=user2,
            # )
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
