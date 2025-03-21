# Create your views here.
from django.shortcuts import render
from django.views import View

from chat.models import ChatMessage


# Create your views here.


def lobby(request):
    return render(request, "chat/lobby.html")


class ChatRoomView(View):
    def get(self, request, room_name="global_chat"):
        """Загружаем страницу чата с сохранёнными сообщениями"""
        messages = ChatMessage.objects.filter(room_name=room_name).order_by("timestamp")
        return render(request, "chat/chat.html", {"room_name": room_name, "messages": messages})
