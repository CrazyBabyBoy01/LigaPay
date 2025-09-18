# orders/services.py

from django.db import transaction

from wallet.models import Wallet


class WalletNotFound(Exception):
    """У пользователя нет кошелька"""


class NotEnoughFunds(Exception):
    """Недостаточно средств"""


class SellerNotFound(Exception):
    """У заказа не указан продавец"""


class BuyerNotFound(Exception):
    """У заказа не указан покупатель"""


class OrderService:
    @staticmethod
    def hold_payment(order):
        """
        Заморозить деньги у покупателя.
        Если всё успешно — обновляем заказ (pending).
        Если ошибка — бросаем исключение.
        """
        try:
            buyer_wallet = Wallet.objects.get(user=order.user)
        except Wallet.DoesNotExist:
            raise WalletNotFound('У пользователя нет кошелька')
        total_price = order.price * order.amount
        if buyer_wallet.balance < total_price:
            raise NotEnoughFunds('Недостаточно средств')
        with transaction.atomic():
            buyer_wallet.balance -= total_price
            buyer_wallet.held_balance += total_price
            buyer_wallet.save()
            order.status = 'pending'
            order.save()

    @staticmethod
    def process_payment(order):
        """
        Списать деньги у покупателя и перевести продавцу.
        Если всё успешно — заказ переходит в статус paid.
        """
        try:
            if not order.seller:
                raise SellerNotFound('У заказа не указан продавец')
            buyer_wallet = Wallet.objects.get(user=order.user)
            seller_wallet = Wallet.objects.get(user=order.seller)
        except Wallet.DoesNotExist:
            raise WalletNotFound('У пользователя нет кошелька')
        total_price = order.price * order.amount
        if buyer_wallet.held_balance < total_price:
            raise NotEnoughFunds('Недостаточно средств')
        with transaction.atomic():
            buyer_wallet.held_balance -= total_price
            buyer_wallet.save()
            seller_wallet.balance += total_price
            seller_wallet.save()
            order.status = 'paid'
            order.save()

    @staticmethod
    def refund(order):
        """
        Вернуть деньги покупателю, если заказ отменён.
        """
        try:
            if not order.user:
                raise BuyerNotFound('У заказа не указан покупатель')
            buyer_wallet = Wallet.objects.get(user=order.user)
        except Wallet.DoesNotExist:
            raise WalletNotFound('У пользователя нет кошелька')
        total_price = order.price * order.amount
        if buyer_wallet.held_balance < total_price:
            raise NotEnoughFunds('Возврат невозможен')
        with transaction.atomic():
            buyer_wallet.held_balance -= total_price
            buyer_wallet.balance += total_price
            buyer_wallet.save()
            order.status = 'canceled'
            order.save()
