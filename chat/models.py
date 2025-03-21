from django.conf import settings
from django.db import models


class ChatMessage(models.Model):
    room_name = models.CharField(max_length=255, default="global_chat")  # Весь чат — это "global_chat"
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.message[:30]}"
