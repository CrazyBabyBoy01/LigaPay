from django.contrib.auth import get_user_model
from django.test import TestCase

from wallet.models import Wallet


User = get_user_model()


class WalletSignalTests(TestCase):
    """Тесты сигналов, связанных с автоматическим созданием кошелька при регистрации пользователя."""

    def test_wallet_created_automatically_when_user_is_created(self):
        """Проверяет, что при создании нового пользователя автоматически создаётся кошелёк."""
        user = User.objects.create_user(username='testuser', password='12345')
        self.assertEqual(Wallet.objects.count(), 1)
        wallet = Wallet.objects.get(user=user)
        self.assertEqual(wallet.user, user)

    def test_wallet_not_duplicated_on_user_update(self):
        """Проверяет, что при повторном сохранении пользователя не создаются дополнительные кошельки."""
        user = User.objects.create_user(username='testuser', password='12345')
        user.save()
        self.assertEqual(Wallet.objects.count(), 1)
        wallet = Wallet.objects.get(user=user)
        self.assertEqual(wallet.user, user)
