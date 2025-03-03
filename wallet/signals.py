from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Wallet


"Это сигнал нужен, для того что бы при регистрации нового пользователя,"
"у него автоматически создавался кошелек,а то пришлось бы создавать вручную для каждого пользователя"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_wallet(sender, instance, created, **kwargs):
    if created:  # Если пользователь только что создан
        Wallet.objects.create(user=instance)
        print(f"Кошелек создан для пользователя {instance.username}")
