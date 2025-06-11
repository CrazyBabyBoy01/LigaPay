from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class ChatRoom(models.Model):
    # СТАРЫЕ ПОЛЯ — временно оставляем
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    service = GenericForeignKey("content_type", "object_id")

    # НОВЫЕ ПОЛЯ — основа для общего чата
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="buyer_chats")
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="seller_chats")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["buyer", "seller"], name="unique_chatroom_buyer_seller")]

    def __str__(self):
        return f"Chat between {self.buyer.username} & {self.seller.username}"


class ChatMessage(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages", null=True, blank=True)
    room_name = models.CharField(max_length=100, null=True, blank=True)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.room_name != "global_chat" and self.chat_room is None:
            raise ValueError("chat_room не может быть NULL для чатов услуг!")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.sender}: {self.message[:30]}"


class DummyModel(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
