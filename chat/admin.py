# Register your models here.
from django.contrib import admin

from .models import ChatMessage, ChatRoom


class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ("content_type", "object_id", "buyer", "seller", "created_at")


class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("chat_room", "sender", "message", "timestamp", "room_name")


admin.site.register(ChatRoom, ChatRoomAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)
