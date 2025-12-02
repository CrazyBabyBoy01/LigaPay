from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Count, OuterRef, Q, Subquery


class ChatRoomQuerySet(models.QuerySet):
    def last_messages(self):
        last_messages = ChatMessage.objects.filter(
            chat_room=OuterRef('pk'),
            chat_room__is_global=False,
        ).order_by('-timestamp')
        return self.annotate(
            last_message_text=Subquery(last_messages.values('message')[:1]),
            last_message_time=Subquery(last_messages.values('timestamp')[:1]),
        ).order_by('-last_message_time')

    def with_unread_counts(self, user):
        return self.annotate(
            unread_count=Count('messages', filter=Q(messages__is_read=False) & ~Q(messages__sender=user))
        )


class ChatRoomManager(models.Manager):
    def get_queryset(self):
        return ChatRoomQuerySet(self.model, using=self._db)

    def for_user(self, user):
        return self.filter(Q(buyer=user) | Q(seller=user))


class ChatRoom(models.Model):
    # СТАРЫЕ ПОЛЯ — временно оставляем
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    service = GenericForeignKey('content_type', 'object_id')
    # НОВЫЕ ПОЛЯ — основа для общего чата

    created_at = models.DateTimeField(auto_now_add=True)
    is_global = models.BooleanField(default=False)
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='buyer_chats',
        null=True,
        blank=True,
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='seller_chats',
        null=True,
        blank=True,
    )
    objects = ChatRoomManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['buyer', 'seller'], name='unique_chatroom_buyer_seller'),
            models.UniqueConstraint(
                fields=['is_global'], condition=models.Q(is_global=True), name='unique_global_chatroom'
            ),
        ]

    def __str__(self):
        if self.is_global:
            return 'Global chat'
        return f'Chat between {self.buyer} & {self.seller}'


class ChatMessage(models.Model):
    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='messages', on_delete=models.CASCADE
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender}: {self.message[:30]}'


class DummyModel(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
