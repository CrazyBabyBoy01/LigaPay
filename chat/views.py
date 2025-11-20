from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render
from django.views import View

from chat.mixin import GroupedMessagesMixin
from chat.models import ChatMessage, ChatRoom

from .utils import get_unread_message_count


def lobby(request):
    """Отображает страницу «лобби» для чата (точка входа в систему чатов)."""
    return render(request, 'chat/lobby.html')


@login_required
def unread_message_count_api(request):
    """API-эндпоинт для получения количества непрочитанных сообщений у пользователя."""
    count = get_unread_message_count(request.user)
    return JsonResponse({'unread_count': count})


class ChatRoomView(View):
    """Загружаем страницу глобального чата с сохранёнными сообщениями."""

    def get(self, request):
        chat_room, _ = ChatRoom.objects.get_or_create(is_global=True)
        messages = chat_room.messages.select_related('sender').order_by('timestamp')
        return render(
            request,
            'chat/lobby.html',
            {
                'chat_room': chat_room,
                'messages': messages,
            },
        )


class DialogsView(LoginRequiredMixin, View):
    """Формируем список всех чатов пользователя с последними сообщениями и количеством непрочитанных."""

    def get(self, request):
        user = request.user

        chat_rooms = (
            ChatRoom.objects.for_user(user)
            .select_related('buyer', 'seller')
            .last_messages()
            .with_unread_counts(user)
        )
        return render(request, 'chat/dialogs.html', {'chat_rooms': chat_rooms})


class DialogDetailView(LoginRequiredMixin, GroupedMessagesMixin, View):
    """Отображение конкретного диалога. Проверка доступа, отметка сообщений прочитанными,
    подготовка списка чатов и сообщений."""

    def get(self, request, chat_id):
        user = request.user

        chat_rooms = (
            ChatRoom.objects.for_user(user)
            .select_related('buyer', 'seller')
            .last_messages()
            .with_unread_counts(user)
        )
        chat = ChatRoom.objects.select_related('buyer', 'seller').get(id=chat_id)
        if request.user != chat.buyer and request.user != chat.seller:
            return HttpResponseForbidden('У вас нет доступа к этому чату')
        ChatMessage.objects.filter(chat_room=chat, is_read=False).exclude(sender=request.user).update(
            is_read=True
        )

        messages = chat.messages.all().order_by('timestamp')
        interlocutor = chat.seller if request.user == chat.buyer else chat.buyer
        pending_order = None
        grouped_messages = self.group_messages(messages)
        return render(
            request,
            'chat/dialogs.html',
            {
                'chat_rooms': chat_rooms,
                'chat': chat,
                'messages': messages,
                'grouped_messages': grouped_messages,
                'buyer': chat.buyer.username,
                'seller': chat.seller.username,
                'interlocutor': interlocutor,
                'pending_order': pending_order,
            },
        )
