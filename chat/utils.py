# Счетчик непрочитанных сообщений
from .models import ChatMessage


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
