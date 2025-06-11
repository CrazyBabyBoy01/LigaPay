from django.urls import path

from . import views


app_name = "chat"
urlpatterns = [
    path("chat/", views.lobby),
    path("chat/unread-count/", views.unread_message_count_api, name="unread_message_count_api"),
    path("", views.ChatRoomView.as_view(), name="chat_room"),  # Конкретный чат по имени комнаты
    path("dialogs/", views.DialogsView.as_view(), name="chat_dialogs"),  # Страница всех диалогов
    path(
        "dialogs/<int:chat_id>/", views.DialogDetailView.as_view(), name="chat_dialog_detail"
    ),  # Переписка с конкретным собеседником
]
