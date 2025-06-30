# Create your views here.
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import OuterRef, Q, Subquery
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from orders.models import Order
from products.mixins import ServiceChatMixin

from chat.mixin import GroupedMessagesMixin
from chat.models import ChatMessage, ChatRoom

from .utils import get_unread_message_count


# Create your views here.


def lobby(request):
    return render(request, "chat/lobby.html")


@login_required
def unread_message_count_api(request):
    count = get_unread_message_count(request.user)
    return JsonResponse({"unread_count": count})


class ChatRoomView(View):
    def get(self, request, room_name="global_chat"):
        """Загружаем страницу чата с сохранёнными сообщениями"""
        messages = ChatMessage.objects.filter(room_name=room_name).order_by("timestamp")
        return render(request, "chat/chat.html", {"room_name": room_name, "messages": messages})


class DialogsView(LoginRequiredMixin, View):
    """Представление для списка чатов пользователя (слева)"""

    def get(self, request):
        user = request.user

        # Все чаты с участием пользователя
        chat_rooms = ChatRoom.objects.filter(buyer=user) | ChatRoom.objects.filter(seller=user)
        chat_rooms = chat_rooms.select_related("buyer", "seller").order_by("-created_at")

        # Subquery для последнего сообщения
        last_messages = ChatMessage.objects.filter(
            chat_room=OuterRef("pk"),  # только сообщения с привязкой к комнате
            room_name__isnull=True,  # исключаем глобальный чат
        ).order_by("-timestamp")

        chat_rooms = chat_rooms.annotate(
            last_message_text=Subquery(last_messages.values("message")[:1]),
            last_message_time=Subquery(last_messages.values("timestamp")[:1]),
        ).order_by("-last_message_time")  # сортировка по последнему сообщению

        return render(request, "chat/dialogs.html", {"chat_rooms": chat_rooms})


class DialogDetailView(LoginRequiredMixin, GroupedMessagesMixin, View):
    """Представление для конкретного диалога (справа)"""

    def get(self, request, chat_id):
        user = request.user
        last_messages = ChatMessage.objects.filter(chat_room=OuterRef("pk"), chat_room__isnull=False).order_by(
            "-timestamp"
        )

        chat_rooms = ChatRoom.objects.filter(buyer=user) | ChatRoom.objects.filter(seller=user)
        chat_rooms = (
            chat_rooms.select_related("buyer", "seller")
            .annotate(
                last_message_text=Subquery(last_messages.values("message")[:1]),
                last_message_time=Subquery(last_messages.values("timestamp")[:1]),
            )
            .order_by("-last_message_time")
        )

        chat = ChatRoom.objects.get(id=chat_id)
        if request.user != chat.buyer and request.user != chat.seller:
            return render(request, "chat/forbidden.html", status=403)
        # ✅ Помечаем входящие сообщения как прочитанные
        ChatMessage.objects.filter(chat_room=chat, is_read=False).exclude(sender=request.user).update(is_read=True)

        messages = chat.messages.all().order_by("timestamp")
        interlocutor = chat.seller if request.user == chat.buyer else chat.buyer
        pending_order = None
        if request.user.is_authenticated:
            pending_order = (
                Order.objects.filter(
                    status="pending",
                )
                .filter(Q(user=chat.buyer, seller=chat.seller) | Q(user=chat.seller, seller=chat.buyer))
                .first()
            )
        grouped_messages = self.group_messages(messages)
        return render(
            request,
            "chat/dialogs.html",
            {
                "chat_rooms": chat_rooms,
                "chat": chat,
                "messages": messages,
                "grouped_messages": grouped_messages,
                "buyer": chat.buyer.username,
                "seller": chat.seller.username,
                "interlocutor": interlocutor,
                "pending_order": pending_order,
            },
        )
