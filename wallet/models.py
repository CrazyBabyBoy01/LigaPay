# Create your models here.
import logging
from decimal import Decimal

from django.conf import settings
from django.db import models, transaction
from django.forms import ValidationError
from django.utils.timezone import now


class NotEnoughFunds(Exception):  # noqa: N818
    """Недостаточно средств"""


logger = logging.getLogger(__name__)


class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet'
    )
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    held_balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f'Wallet({self.user.username} - {self.balance})'

    def _normalize_amount(self, amount):
        amount = Decimal(amount).quantize(Decimal('0.01'))
        if amount <= 0:
            raise ValidationError('Сумма должна быть положительной.')
        return amount

    def deposit(self, amount):
        """
        Пополнение баланса.
        Создаёт транзакцию 'deposit'.
        Бросает ValidationError, если сумма некорректна.
        """
        amount = self._normalize_amount(amount)
        self.balance += amount
        self.save()
        Transaction.objects.create(wallet=self, amount=amount, transaction_type='deposit')

    def withdraw(self, amount):
        """
        Списание средств с баланса.
        Создаёт транзакцию 'withdraw'.
        Бросает NotEnoughFunds, если денег недостаточно.
        """
        amount = self._normalize_amount(amount)
        if self.balance < amount:
            logger.warning(
                'Недостаточно средств на балансе. wallet=%s, balance=%s, attempted=%s',
                self.id,
                self.balance,
                amount,
            )
            raise ValidationError('Недостаточно средств на балансе.')
        self.balance -= amount
        self.save()
        Transaction.objects.create(wallet=self, amount=-amount, transaction_type='withdraw')

    def hold(self, amount):
        """
        Замораживает деньги на балансе.
        Переносит сумму из balance в held_balance.
        Создаёт транзакцию 'hold'.
        """
        amount = self._normalize_amount(amount)
        if self.balance < amount:
            raise NotEnoughFunds('Недостаточно средств')
        with transaction.atomic():
            self.balance -= amount
            self.held_balance += amount
            self.save()
            Transaction.objects.create(wallet=self, amount=-amount, transaction_type='hold')

    def release_to(self, amount, recipient_wallet):
        """
        Перевод замороженных средств продавцу.
        Уменьшает held_balance покупателя и увеличивает balance продавца.
        Создаёт транзакции 'purchase' и 'sale'.
        """
        amount = self._normalize_amount(amount)
        if self.held_balance < amount:
            raise NotEnoughFunds('Недостаточно средств')
        with transaction.atomic():
            self.held_balance -= amount
            self.save()
            recipient_wallet.balance += amount
            recipient_wallet.save()
            Transaction.objects.create(wallet=self, amount=-amount, transaction_type='purchase')
            Transaction.objects.create(wallet=recipient_wallet, amount=amount, transaction_type='sale')

    def refund(self, amount):
        """
        Возврат замороженных средств покупателю.
        Уменьшает held_balance и увеличивает balance.
        Создаёт транзакцию 'refund'.
        """
        amount = self._normalize_amount(amount)
        if self.held_balance < amount:
            raise NotEnoughFunds('Возврат невозможен')
        with transaction.atomic():
            self.held_balance -= amount
            self.balance += amount
            self.save()
            Transaction.objects.create(wallet=self, amount=amount, transaction_type='refund')


"""История транзакций"""


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('deposit', 'Пополнение'),
        ('withdraw', 'Вывод'),
        ('sale', 'Продажа'),
        ('purchase', 'Покупка'),
        ('refund', 'Возврат'),
        ('hold', 'Заморозка'),
    )
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f'{self.get_transaction_type_display()} {self.amount} для {self.wallet.user.username}'


'ForeignKey(Wallet, on_delete=models.CASCADE) – если удалить кошелёк, удалятся и все его транзакции.'
'amount – сумма транзакции.'
'transaction_type – тип (deposit, withdraw, purchase, refund).'
'timestamp – время создания транзакции (по умолчанию now()).'
