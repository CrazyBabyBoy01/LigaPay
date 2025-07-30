from decimal import Decimal

from django.conf import settings
from django.db import models, transaction
from django.forms import ValidationError
from django.utils.timezone import now


# Create your models here.


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    held_balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    def deposit(self, amount):
        """Пополнение баланса"""
        amount = Decimal(amount).quantize(Decimal("0.01"))
        if amount <= 0:
            raise ValidationError("Сумма пополнения должна быть положительной.")
        self.balance += amount
        self.save()
        Transaction.objects.create(wallet=self, amount=amount, transaction_type="deposit")

    def withdraw(self, amount):
        """Списание средств"""
        amount = Decimal(amount).quantize(Decimal("0.01"))
        if amount <= 0:
            raise ValidationError("Сумма списания должна быть положительной.")
        if self.balance < amount:
            raise ValidationError("Недостаточно средств на балансе.")
        self.balance -= amount
        self.save()
        print(f"==> Balance after withdraw: {self.balance}")
        Transaction.objects.create(wallet=self, amount=-amount, transaction_type="withdraw")

    def transfer(self, recipient_wallet, amount):
        """Перевод денег другому пользователю"""
        if recipient_wallet == self:
            raise ValidationError("Нельзя переводить деньги самому себе.")
        with transaction.atomic():
            self.withdraw(amount)
            recipient_wallet.deposit(amount)
        Transaction.objects.create(wallet=self, amount=-amount, transaction_type="transfer_out")
        Transaction.objects.create(wallet=recipient_wallet, amount=amount, transaction_type="transfer_in")

    def __str__(self):
        return f"Wallet({self.user.username} - {self.balance})"


"""История транзакций"""


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ("deposit", "Пополнение"),
        ("withdraw", "Вывод"),
        ("purchase", "Покупка"),
        ("refund", "Возврат"),
    )
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.get_transaction_type_display()} {self.amount} для {self.wallet.user.username}"


"ForeignKey(Wallet, on_delete=models.CASCADE) – если удалить кошелёк, удалятся и все его транзакции."
"amount – сумма транзакции."
"transaction_type – тип (deposit, withdraw, purchase, refund)."
"timestamp – время создания транзакции (по умолчанию now())."
