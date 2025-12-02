from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from orders.models import Order
from orders.services import OrderService, SellerNotFound, WalletNotFound
from products.models import AccountService, Category
from wallet.models import Wallet


User = get_user_model()


class OrderServiceTest(TestCase):
    """Тесты бизнес-логики OrderService."""

    def _create_test_service(self, model=AccountService, **kwargs):
        """
        Вспомогательный метод для создания тестового объекта.

        """
        user = User.objects.create_user(username='user', email='test1@example.com', password='pass123')
        seller = User.objects.create_user(
            username='seller', email='test2@example.com', password='pass123'
        )
        category = Category.objects.create(name='product5', slug='product_slug4')
        product = model.objects.create(
            title='Rp', seller=user, price=100, category=category, quantity=5, **kwargs
        )
        content_type = ContentType.objects.get_for_model(AccountService)
        defaults = {
            'user': user,
            'seller': seller,
            'content_type': content_type,
            'object_id': product.id,
            'amount': 1,
            'price': product.price,
        }
        defaults.update(kwargs)
        return user, seller, product, Order.objects.create(**defaults)

    @patch('orders.services.Wallet.objects.get')
    @patch('orders.services.Wallet.hold')
    def test_hold_payment_success(self, mock_hold, mock_get):
        """Проверяет, что при успешном замораживании денег заказ переходит в статус 'pending'."""
        _, _, _, order = self._create_test_service()
        mock_wallet = MagicMock()
        mock_get.return_value = mock_wallet
        OrderService.hold_payment(order)
        mock_get.assert_called_once_with(user=order.user)
        self.assertEqual(order.status, 'pending')
        mock_wallet.hold.assert_called_once()

    @patch('orders.services.Wallet.objects.get')
    def test_hold_payment_wallet_not_found(self, mock_get):
        """Проверяет, что если у пользователя нет кошелька, выбрасывается WalletNotFound."""
        _, _, _, order = self._create_test_service()
        mock_get.side_effect = Wallet.DoesNotExist
        with self.assertRaises(WalletNotFound):
            OrderService.hold_payment(order)
        mock_get.assert_called_once_with(user=order.user)

    def test_process_payment_success(self):
        """Проверяет, что при успешной оплате вызывается release_to и заказ становится 'paid'."""
        user, seller, _, order = self._create_test_service()
        wallet = Wallet.objects.get(user=user)
        wallet.held_balance = 1000
        wallet.save()
        OrderService.process_payment(order)
        self.assertEqual(order.status, 'paid')

    def test_process_payment_seller_not_found(self):
        """Проверяет, что если у заказа нет продавца, выбрасывается SellerNotFound."""
        user, seller, _, order = self._create_test_service()
        order.seller = None
        order.save()
        with self.assertRaises(SellerNotFound):
            OrderService.process_payment(order)

    @patch('orders.services.Wallet.objects.get')
    def test_process_payment_wallet_not_found(self, mock_get):
        """Проверяет, что если у кого-то из участников нет кошелька, выбрасывается WalletNotFound."""
        _, _, _, order = self._create_test_service()
        mock_get.side_effect = Wallet.DoesNotExist
        with self.assertRaises(WalletNotFound):
            OrderService.process_payment(order)
        self.assertEqual(mock_get.call_count, 1)
        mock_get.assert_called_with(user=order.user)
        self.assertEqual(order.status, 'pending')

    def test_refund_success(self):
        """Проверяет, что при возврате денег вызывается refund и заказ становится 'canceled'."""
        user, _, _, order = self._create_test_service()
        wallet = Wallet.objects.get(user=user)
        wallet.held_balance = 1000
        wallet.save()
        OrderService.refund(order)
        self.assertEqual(order.status, 'canceled')

    def test_refund_wallet_not_found(self):
        """Проверяет, что при отсутствии кошелька выбрасывается WalletNotFound."""
        user, _, _, order = self._create_test_service()
        Wallet.objects.filter(user=user).delete()
        with self.assertRaises(WalletNotFound):
            OrderService.refund(order)
