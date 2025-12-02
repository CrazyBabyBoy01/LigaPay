from decimal import Decimal

from django.contrib.auth import get_user_model
from django.forms import ValidationError
from django.test import TestCase

from wallet.models import NotEnoughFunds, Transaction, Wallet


User = get_user_model()


class WalletModelTests(TestCase):
    """Тесты бизнес-логики модели Wallet (без проверки кода Django)."""

    def setUp(self):
        """Создаёт пользователя и кошелёк перед каждым тестом."""
        self.user = User.objects.create_user(
            username='testuser', password='12345', email='test1@example.com'
        )
        self.wallet = Wallet.objects.get(user=self.user)
        self.seller = User.objects.create_user(
            username='seller', password='12345', email='test2@example.com'
        )
        self.seller_wallet = Wallet.objects.get(user=self.seller)

    def test_normalize_amount_positive_value(self):
        """Проверяет, что _normalize_amount возвращает округлённую сумму и выбрасывает ошибку для <= 0.
        """
        result = self.wallet._normalize_amount('10.506')
        self.assertEqual(result, Decimal('10.51'))
        with self.assertRaises(ValidationError):
            self.wallet._normalize_amount(0)
        with self.assertRaises(ValidationError):
            self.wallet._normalize_amount(-5)

    def test_deposit_increases_balance_and_creates_transaction(self):
        """Проверяет, что deposit увеличивает баланс и создаёт транзакцию типа 'deposit'."""
        self.wallet.deposit(100)
        self.wallet.refresh_from_db()
        self.assertEqual(Transaction.objects.count(), 1)
        transaction = Transaction.objects.first()
        self.assertEqual(transaction.transaction_type, 'deposit')
        self.assertEqual(self.wallet.balance, Decimal('100.00'))

    def test_withdraw_decreases_balance_and_creates_transaction(self):
        """Проверяет, что withdraw уменьшает баланс и создаёт транзакцию 'withdraw'."""
        self.wallet.balance = Decimal('300.00')
        self.wallet.withdraw(100)
        self.assertEqual(Transaction.objects.count(), 1)
        transaction = Transaction.objects.first()
        self.assertEqual(transaction.transaction_type, 'withdraw')
        self.assertEqual(self.wallet.balance, Decimal('200.00'))

    def test_withdraw_raises_error_if_not_enough_balance(self):
        """Проверяет, что withdraw выбрасывает ValidationError при недостатке средств."""
        with self.assertRaises(ValidationError):
            self.wallet.withdraw(100)

    def test_hold_moves_balance_to_held_and_creates_transaction(self):
        """Проверяет, что hold уменьшает balance, увеличивает held_balance и создаёт транзакцию 'hold'.
        """
        self.wallet.balance = Decimal('300.00')
        self.wallet.hold(100)
        self.assertEqual(Transaction.objects.count(), 1)
        transaction = Transaction.objects.first()
        self.assertEqual(transaction.transaction_type, 'hold')
        self.assertEqual(self.wallet.balance, Decimal('200.00'))
        self.assertEqual(self.wallet.held_balance, Decimal('100.00'))

    def test_hold_raises_not_enough_funds(self):
        """Проверяет, что hold выбрасывает NotEnoughFunds при нехватке средств."""
        with self.assertRaises(NotEnoughFunds):
            self.wallet.hold(100)

    def test_release_to_transfers_funds_between_wallets(self):
        """Проверяет, что release_to уменьшает held_balance покупателя и увеличивает balance продавца."""

        self.wallet.held_balance = Decimal('300.00')
        self.wallet.release_to(300, self.seller_wallet)
        self.assertEqual(Transaction.objects.count(), 2)
        transaction = Transaction.objects.first()
        self.assertEqual(transaction.transaction_type, 'purchase')
        self.assertEqual(self.seller_wallet.balance, Decimal('300.00'))
        self.assertEqual(self.wallet.held_balance, Decimal('0'))

    def test_release_to_raises_not_enough_funds(self):
        """
        Проверяет, что release_to выбрасывает NotEnoughFunds, если held_balance меньше суммы перевода.
        """
        with self.assertRaises(NotEnoughFunds):
            self.wallet.release_to(100, self.seller_wallet)

    def test_refund_returns_held_to_balance(self):
        """Проверяет, что refund возвращает деньги из held_balance обратно в balance."""
        self.wallet.held_balance = Decimal('300.00')
        self.wallet.refund(150)
        self.assertEqual(Transaction.objects.count(), 1)
        transaction = Transaction.objects.first()
        self.assertEqual(transaction.transaction_type, 'refund')
        self.assertEqual(self.wallet.balance, Decimal('150.00'))
        self.assertEqual(self.wallet.held_balance, Decimal('150.00'))

    def test_refund_raises_not_enough_funds(self):
        """Проверяет, что refund выбрасывает NotEnoughFunds, если замороженных средств недостаточно."""
        with self.assertRaises(NotEnoughFunds):
            self.wallet.refund(150)
