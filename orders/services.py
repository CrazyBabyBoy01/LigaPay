# orders/services.py

from django.db import transaction

from wallet.models import Wallet


class WalletNotFound(Exception):
    """У пользователя нет кошелька"""


class SellerNotFound(Exception):
    """У заказа не указан продавец"""


class BuyerNotFound(Exception):
    """У заказа не указан покупатель"""


class NotEnoughFunds(Exception):
    """Недостаточно средств"""


class OrderService:
    @staticmethod
    def hold_payment(order):
        """
        Заморозить деньги у покупателя.
        Если всё успешно — обновляем заказ (pending).
        Если ошибка — бросаем исключение.
        """
        with transaction.atomic():
            try:
                buyer_wallet = Wallet.objects.get(user=order.user)
            except Wallet.DoesNotExist:
                raise WalletNotFound('У пользователя нет кошелька')
            total_price = order.price * order.amount
            buyer_wallet.hold(total_price)
            order.status = 'pending'
            order.save()

    @staticmethod
    def process_payment(order):
        """
        Списать деньги у покупателя и перевести продавцу.
        Если всё успешно — заказ переходит в статус paid.
        """
        with transaction.atomic():
            if not order.seller:
                raise SellerNotFound('У заказа не указан продавец')
            try:
                buyer_wallet = Wallet.objects.get(user=order.user)
                seller_wallet = Wallet.objects.get(user=order.seller)
            except Wallet.DoesNotExist:
                raise WalletNotFound('У пользователя нет кошелька')
            total_price = order.price * order.amount
            buyer_wallet.release_to(total_price, seller_wallet)
            order.status = 'paid'
            order.save()

    @staticmethod
    def refund(order):
        """
        Вернуть деньги покупателю, если заказ отменён.
        """
        with transaction.atomic():
            if not order.user:
                raise BuyerNotFound('У заказа не указан покупатель')
            try:
                buyer_wallet = Wallet.objects.get(user=order.user)
            except Wallet.DoesNotExist:
                raise WalletNotFound('У пользователя нет кошелька')
            total_price = order.price * order.amount
            buyer_wallet.refund(total_price)
            order.status = 'canceled'
            order.save()
