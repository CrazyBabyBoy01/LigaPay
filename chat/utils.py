# Счетчик непрочитанных сообщений
from channels.consumer import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.middleware.csrf import get_token

from .models import ChatMessage, ChatRoom


User = get_user_model()


def get_unread_message_count(user):
    # Для покупателя
    buyer_messages = (
        ChatMessage.objects.filter(
            chat_room__buyer=user  # Ищем чаты, где пользователь - покупатель
        )
        .exclude(sender=user)
        .filter(is_read=False)
        .count()
    )  # Исключаем сообщения от пользователя и считаем непрочитанные

    # Для продавца
    seller_messages = (
        ChatMessage.objects.filter(
            chat_room__seller=user  # Ищем чаты, где пользователь - продавец
        )
        .exclude(sender=user)
        .filter(is_read=False)
        .count()
    )  # Исключаем сообщения от пользователя и считаем непрочитанные

    # Складываем количество непрочитанных сообщений
    return buyer_messages + seller_messages


def get_or_create_chat(buyer, seller):
    user1, user2 = sorted([buyer, seller], key=lambda u: u.id)

    chat_room = (
        ChatRoom.objects.filter(Q(buyer=user1, seller=user2) | Q(buyer=user2, seller=user1))
        .select_related('buyer', 'seller')
        .first()
    )

    if not chat_room:
        chat_room = ChatRoom.objects.create(buyer=user1, seller=user2)
    return chat_room


def send_chat_event(chat_room, order, message_text, request=None, event_type=None):
    system_user = User.objects.get(username='LigaPay')
    ChatMessage.objects.create(
        chat_room=chat_room,
        sender=system_user,
        message=message_text,
    )
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'chat_{chat_room.id}',
        {
            'type': 'chat_message',
            'message': message_text,
            'sender': system_user.username,
            'order_id': order.id,
            'is_system': True,
        },
    )
    if event_type:
        if request:
            # Потом сигнал клиенту отрисовать кнопку
            async_to_sync(channel_layer.group_send)(
                f'chat_{chat_room.id}',
                {
                    'type': event_type,
                    'order_id': order.id,
                    'csrf_token': get_token(request),
                    'buyer_username': order.user.username,
                    'seller_username': order.seller.username,
                },
            )
        else:
            async_to_sync(channel_layer.group_send)(
                f'chat_{chat_room.id}',
                {
                    'type': event_type,  # 👈 вот оно
                    'message': 'Покупка подтверждена и оплачена!',
                    'order_id': order.id,
                },
            )
