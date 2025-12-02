from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from wallet.models import Transaction, Wallet


User = get_user_model()


class DepositViewTests(TestCase):
    """Тесты бизнес-логики представления DepositView (пополнение кошелька)."""

    def setUp(self):
        """Создаёт пользователя и авторизует его перед каждым тестом."""
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.wallet = Wallet.objects.get(user=self.user)
        self.client.login(username='testuser', password='12345')
        self.url = reverse('wallet:wallet_deposit')

    def test_successful_post_increases_balance_and_redirects(self):
        """Проверяет, что при корректной сумме баланс увеличивается и происходит редирект."""
        response = self.client.post(self.url, {'amount': '100'})
        self.wallet.refresh_from_db()
        transaction = Transaction.objects.first()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(transaction.transaction_type, 'deposit')
        self.assertEqual(self.wallet.balance, Decimal('100.00'))

    def test_invalid_post_shows_error_and_does_not_change_balance(self):
        """Проверяет, что при неверной сумме показывается ошибка и баланс не изменяется."""
        response = self.client.post(self.url, {'amount': '-100'})
        self.wallet.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Transaction.objects.count(), 0)
        self.assertEqual(self.wallet.balance, Decimal('0.00'))
        self.assertContains(response, 'Сумма должна быть положительной')
