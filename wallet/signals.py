import logging

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Wallet


logger = logging.getLogger(__name__)

'Это сигнал нуженcxz, для того что бы при регистрации нового пользователя,'
'у него автоматически создавался кошелек,а то пришлось бы создавать вручную для каждого пользователя'


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_wallet(sender, instance, created, **kwargs):
    if created:  # Если пользователь только что создан
        Wallet.objects.get_or_create(user=instance)
        logger.info('Кошелёк создан для пользователя %s', instance.username)
