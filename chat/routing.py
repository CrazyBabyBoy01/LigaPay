from django.urls import re_path

from chat import consumers  # Будем использовать ChatConsumer, который обработает сообщения


websocket_urlpatterns = [
    re_path(r"ws/socket-server/", consumers.ChatConsumer.as_asgi()),  # Маршрут для чата
    # re_path(r"ws/chat/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
]
