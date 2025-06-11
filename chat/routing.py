from django.urls import re_path

from chat import consumers  # Будем использовать ChatConsumer, который обработает сообщения


websocket_urlpatterns = [
    # 🔹 Общий чат (один маршрут для всего проекта)
    re_path(r"ws/chat/global_chat/$", consumers.ChatConsumer.as_asgi()),
    # 🔹 Личный чат между пользователями (по ID чата)
    re_path(r"ws/chat/dialogs/(?P<chat_id>\d+)/$", consumers.ChatConsumer.as_asgi()),
    # 🔹 Чат для услуги (например: ws://127.0.0.1:8000/ws/chat/rpservice/1/)
    re_path(r"ws/chat/(?P<service_type>[\w-]+)/(?P<service_id>\d+)/$", consumers.ChatConsumer.as_asgi()),
]
