from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from orders.models import Order, Review
from orders.services import NotEnoughFunds, WalletNotFound
from products.models import AccountService, Category
from wallet.models import Wallet


User = get_user_model()


class CreateOrderViewTest(TestCase):
    """Тесты логики создания заказа."""

    def _create_test_service(self, model=AccountService, **kwargs):
        """
        Вспомогательный метод для создания тестового объекта.
        """
        user = User.objects.create_user(
            username='newuser1', email='test1@example.com', password='pass123'
        )
        category = Category.objects.create(name='product5', slug='product_slug4')
        product = model.objects.create(
            title='Acc', seller=user, price=100, category=category, quantity=5, **kwargs
        )
        return user, product

    @patch('orders.views.send_chat_event')
    @patch('orders.views.get_or_create_chat')
    @patch('orders.models.Order.hold_payment')
    def test_create_order_success(self, mock_hold, mock_chat, mock_send):
        """Проверяет, что при валидных данных создаётся заказ и вызывается hold_payment."""
        user, product = self._create_test_service()
        self.client.force_login(user)
        url = reverse(
            'orders:create_order', kwargs={'model_name': 'AccountService', 'product_id': product.id}
        )
        data = {
            'payment_method': 'method1',
            'player_id': '123456',
            'amount': 1,
            'price': 100,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        mock_hold.assert_called_once()
        mock_chat.return_value = None
        mock_send.return_value = None
        self.assertEqual(Order.objects.count(), 1)

    def test_create_order_invalid_form(self):
        """Проверяет, что при невалидной форме возвращается ошибка и заказ не создаётся."""
        user, product = self._create_test_service()
        self.client.force_login(user)
        url = reverse(
            'orders:create_order', kwargs={'model_name': 'AccountService', 'product_id': product.id}
        )
        data = {
            'payment_method': 'adsd',
            'player_id': '123456',
            'amount': 1,
            'price': 100,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.count(), 0)

    @patch('orders.views.CreateOrderView._get_product', return_value=None)
    def test_create_order_product_not_found(self, mock_product):
        """Проверяет, что если продукт не найден, возвращается JsonResponse с ошибкой."""
        user, product = self._create_test_service()
        self.client.force_login(user)
        url = reverse(
            'orders:create_order', kwargs={'model_name': 'AccountService', 'product_id': product.id}
        )
        data = {
            'payment_method': 'method1',
            'player_id': '123456',
            'amount': 1,
            'price': 100,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['success'])
        self.assertIn('Товар', response.json()['message'])

    def test_create_order_not_enough_quantity(self):
        """Проверяет, что если запрошено больше товара, чем есть, возвращается сообщение об ошибке."""
        user, product = self._create_test_service()
        self.client.force_login(user)
        url = reverse(
            'orders:create_order', kwargs={'model_name': 'AccountService', 'product_id': product.id}
        )
        data = {
            'payment_method': 'method1',
            'player_id': '123456',
            'amount': 6,
            'price': 100,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['success'])
        self.assertIn('Недостаточное', response.json()['message'])
        self.assertEqual(Order.objects.count(), 0)

    @patch('orders.models.Order.hold_payment')
    def test_create_order_not_enough_funds(self, mock_hold):
        """Проверяет, что при недостатке средств вызывается NotEnoughFunds и заказ удаляется."""
        user, product = self._create_test_service()
        self.client.force_login(user)
        url = reverse(
            'orders:create_order', kwargs={'model_name': 'AccountService', 'product_id': product.id}
        )
        data = {
            'payment_method': 'method1',
            'player_id': '123456',
            'amount': 1,
            'price': 100,
        }
        mock_hold.side_effect = NotEnoughFunds
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['success'])

        self.assertIn('Недостаточно', response.json()['message'])
        self.assertEqual(Order.objects.count(), 0)

    def test_create_order_wallet_not_found(self):
        """Проверяет, что при отсутствии кошелька вызывается WalletNotFound и заказ удаляется."""
        user, product = self._create_test_service()
        Wallet.objects.filter(user=user).delete()
        self.client.force_login(user)
        url = reverse(
            'orders:create_order', kwargs={'model_name': 'AccountService', 'product_id': product.id}
        )
        data = {
            'payment_method': 'method1',
            'player_id': '123456',
            'amount': 1,
            'price': 100,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['success'])
        self.assertIn('кошел', response.json()['message'])

    @patch('orders.views.send_chat_event')
    @patch('orders.views.get_or_create_chat')
    @patch('orders.models.Order.hold_payment')
    def test_create_order_triggers_chat_event(self, mock_send, mock_chat, mock_hold):
        """Проверяет, что при успешном создании заказа отправляется событие в чат."""
        user, product = self._create_test_service()
        self.client.force_login(user)
        url = reverse(
            'orders:create_order', kwargs={'model_name': 'AccountService', 'product_id': product.id}
        )
        data = {
            'payment_method': 'method1',
            'player_id': '123456',
            'amount': 1,
            'price': 100,
        }
        response = self.client.post(url, data)
        mock_chat.assert_called_once()
        mock_send.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])


class ConfirmOrderViewTest(TestCase):
    """Тесты подтверждения оплаты заказа."""

    def _create_test_order(self, model=AccountService, **kwargs):
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

    @patch('orders.views.send_chat_event')
    @patch('orders.views.get_or_create_chat')
    @patch('orders.models.Order.process_payment')
    def test_confirm_order_success(self, mock_process, mock_chat, mock_send):
        """Проверяет, что при успешном подтверждении заказа вызываются все необходимые методы и
        возвращается корректный успешный ответ."""
        user, _, _, order = self._create_test_order()
        self.client.force_login(user)
        mock_chat.return_value = 'fake_chat_room'
        url = reverse('orders:confirm_order', kwargs={'order_id': order.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        mock_process.assert_called_once()
        mock_chat.assert_called_once()
        mock_send.assert_called_once()

    @patch('orders.views.send_chat_event')
    @patch('orders.views.get_or_create_chat')
    @patch('orders.models.Order.process_payment')
    def test_confirm_order_already_paid(self, mock_process, mock_chat, mock_send):
        """Проверяет, что нельзя подтвердить заказ со статусом 'paid' или 'canceled'."""
        user, _, _, order = self._create_test_order()
        order.status = 'paid'
        order.save()
        self.client.force_login(user)
        mock_chat.return_value = 'fake_chat_room'
        url = reverse('orders:confirm_order', kwargs={'order_id': order.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['success'])
        self.assertIn('подтвержден', response.json()['message'])

    @patch('orders.models.Order.process_payment')
    def test_confirm_order_not_enough_funds(self, mock_process):
        """Проверяет, что при недостатке средств возвращается корректное сообщение."""
        user, _, _, order = self._create_test_order()
        mock_process.side_effect = NotEnoughFunds
        self.client.force_login(user)
        url = reverse('orders:confirm_order', kwargs={'order_id': order.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['success'])
        self.assertIn('Недостаточно', response.json()['message'])

    @patch('orders.models.Order.process_payment')
    def test_confirm_order_wallet_not_found(self, mock_process):
        """Проверяет, что при отсутствии кошелька возвращается ошибка."""
        user, _, _, order = self._create_test_order()
        mock_process.side_effect = WalletNotFound
        self.client.force_login(user)
        url = reverse('orders:confirm_order', kwargs={'order_id': order.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['success'])
        self.assertIn('нет кошелька', response.json()['message'])

    @patch('orders.models.Order.process_payment')
    @patch('orders.views.get_or_create_chat', return_value=None)
    @patch('orders.views.send_chat_event')
    def test_confirm_order_chat_not_found(self, mock_send, mock_chat, mock_process):
        """Проверяет, что если чат не найден, возвращается success=True, но с предупреждением."""
        user, _, _, order = self._create_test_order()
        self.client.force_login(user)
        url = reverse('orders:confirm_order', kwargs={'order_id': order.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertIn('но чат', response.json()['message'])
        mock_send.assert_not_called()


class CancelOrderViewTest(TestCase):
    """Тесты отмены заказа продавцом."""

    def _create_test_order(self, model=AccountService, **kwargs):
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

    @patch('orders.views.send_chat_event')
    @patch('orders.views.get_or_create_chat')
    @patch('orders.models.Order.refund')
    def test_cancel_order_success(self, mock_refund, mock_chat, mock_send):
        """Проверяет, что продавец может отменить заказ и вызывается refund()."""
        _, seller, _, order = self._create_test_order()
        self.client.force_login(seller)
        mock_chat.return_value = 'fake_chat_room'
        url = reverse('orders:cancel_order', kwargs={'order_id': order.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertIn('отклонён', response.json()['message'])
        mock_refund.assert_called_once()
        mock_chat.assert_called_once()
        mock_send.assert_called_once()

    @patch('orders.models.Order.refund')
    def test_cancel_order_not_seller(self, mock_refund):
        """Проверяет, что пользователь, не являющийся продавцом, не может отменить заказ."""
        user, _, _, order = self._create_test_order()
        self.client.force_login(user)
        url = reverse('orders:cancel_order', kwargs={'order_id': order.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['success'])
        self.assertIn('не можете', response.json()['message'])
        mock_refund.assert_not_called()

    @patch('orders.models.Order.refund')
    def test_cancel_order_completed(self, mock_refund):
        """Проверяет, что нельзя отменить заказ со статусом 'paid' или 'canceled'."""

        _, seller, _, order = self._create_test_order()
        self.client.force_login(seller)
        order.status = 'paid'
        order.save()
        url = reverse('orders:cancel_order', kwargs={'order_id': order.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['success'])
        self.assertIn('Нельзя отменить завершённый заказ.', response.json()['message'])
        mock_refund.assert_not_called()

    @patch('orders.models.Order.refund')
    def test_cancel_order_wallet_not_found(self, mock_refund):
        """Проверяет, что при отсутствии кошелька вызывается WalletNotFound."""
        _, seller, _, order = self._create_test_order()
        self.client.force_login(seller)
        url = reverse('orders:cancel_order', kwargs={'order_id': order.id})
        mock_refund.side_effect = WalletNotFound
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['success'])
        self.assertIn('нет кошелька', response.json()['message'])
        mock_refund.assert_called_once()

    @patch('orders.views.send_chat_event')
    @patch('orders.views.get_or_create_chat', return_value=None)
    @patch('orders.models.Order.refund')
    def test_cancel_order_chat_not_found(self, mock_refund, mock_chat, mock_send):
        """Проверяет, что если чат не найден, возвращается success=True с предупреждением."""
        _, seller, _, order = self._create_test_order()
        self.client.force_login(seller)
        url = reverse('orders:cancel_order', kwargs={'order_id': order.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertIn('Заказ отменён, но чат не найден', response.json()['message'])
        mock_refund.assert_called_once()


class ReviewCreateViewTest(TestCase):
    """Тесты логики создания отзывов пользователем."""

    def _create_test_review(self, model=AccountService, **kwargs):
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

    def test_create_review_success(self):
        """Проверяет, что при корректных данных создаётся отзыв к своему заказу."""
        user, seller, _, order = self._create_test_review()
        self.client.force_login(user)
        url = reverse('orders:review_create')
        data = {
            'order_id': order.id,
            'rating': 5,
            'comment': 'Отличный сервис!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 1)
        review = Review.objects.first()
        self.assertEqual(review.author, user)
        self.assertEqual(review.order, order)
        self.assertEqual(review.rating, 5)

    def test_invalid_order_id(self):
        """Проверяет, что при некорректном order_id происходит редирект и отзыв не создаётся."""
        user, seller, _, order = self._create_test_review()
        self.client.force_login(user)
        url = reverse('orders:review_create')
        data = {
            'order_id': 'djlfjsl',
            'rating': 5,
            'comment': 'Отличный сервис!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 0)

    def test_not_user_order(self):
        """Проверяет, что пользователь не может оставить отзыв к чужому заказу."""
        _, seller, _, order = self._create_test_review()
        user_1 = User.objects.create_user(username='user1', email='test12@example.com')
        self.client.force_login(user_1)
        url = reverse('orders:review_create')
        data = {
            'order_id': order.id,
            'rating': 5,
            'comment': 'Отличный сервис!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 0)

    def test_duplicate_review(self):
        """Проверяет, что повторный отзыв для того же заказа не создаётся."""
        user, seller, _, order = self._create_test_review()
        self.client.force_login(user)
        url = reverse('orders:review_create')
        data = {
            'order_id': order.id,
            'rating': 5,
            'comment': 'Отличный сервис!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 1)
        data = {
            'order_id': order.id,
            'rating': 5,
            'comment': 'Отличный сервис!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 1)

    def test_invalid_rating(self):
        """Проверяет, что при некорректной оценке отзыв не создаётся."""
        user, seller, _, order = self._create_test_review()
        self.client.force_login(user)
        url = reverse('orders:review_create')
        data = {
            'order_id': order.id,
            'rating': 'sda',
            'comment': 'Отличный сервис!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 0)
