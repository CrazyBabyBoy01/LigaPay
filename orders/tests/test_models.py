from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from orders.models import Order, Review
from products.models import AccountService, Category
from wallet.models import Wallet


User = get_user_model()


class OrderModelTest(TestCase):
    """Тесты модели Order."""

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

    def test_order_creation(self):
        """Проверяет, что заказ создаётся корректно с обязательными полями."""
        user, seller, product, order = self._create_test_service()
        self.assertEqual(order.user, user)
        self.assertEqual(order.seller, seller)
        self.assertEqual(order.object_id, product.id)
        self.assertEqual(order.price, product.price)

    def test_delete_user_cascade(self):
        """Убеждается, что при удалении покупателя заказы тоже удаляются."""
        user, _, _, _ = self._create_test_service()
        self.assertEqual(Order.objects.count(), 1)
        user.delete()
        self.assertEqual(Order.objects.count(), 0)

    def test_delete_seller_set_null(self):
        """Проверяет, что при удалении продавца поле seller становится NULL."""
        user, seller, _, order = self._create_test_service()
        self.assertEqual(order.seller, seller)
        seller.delete()
        order.refresh_from_db()
        self.assertIsNone(order.seller)

    def test_str_representation(self):
        """Проверяет корректность строкового представления заказа."""
        _, _, _, order = self._create_test_service()
        self.assertEqual(str(order), f'Заказ {order.id} - {order.product} ({order.status})')

    def test_process_payment_changes_status(self):
        """Проверяет, что после process_payment статус заказа становится 'paid'."""
        user, _, _, order = self._create_test_service()
        wallet = Wallet.objects.get(user=user)
        wallet.held_balance = 1000
        wallet.save()

        self.assertEqual(order.status, 'pending')
        order.process_payment()
        order.refresh_from_db()
        self.assertEqual(order.status, 'paid')

    def test_refund_changes_status(self):
        """Проверяет, что при refund статус меняется на 'canceled'."""
        user, _, _, order = self._create_test_service()
        wallet = Wallet.objects.get(user=user)
        wallet.held_balance = 1000
        wallet.save()
        self.assertEqual(order.status, 'pending')
        order.refund()
        order.refresh_from_db()
        self.assertEqual(order.status, 'canceled')


class ReviewModelTest(TestCase):
    """Тесты модели Review."""

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
            title='Rp', seller=seller, price=100, category=category, quantity=5, **kwargs
        )
        content_type = ContentType.objects.get_for_model(AccountService)
        defaults_1 = {
            'user': user,
            'seller': seller,
            'content_type': content_type,
            'object_id': product.id,
            'amount': 1,
            'price': product.price,
        }
        defaults_1.update(kwargs)
        order = Order.objects.create(**defaults_1)
        defaults_2 = {
            'order': order,
            'author': user,
            'seller': seller,
            'rating': 1,
            'comment': 'ksadh',
        }
        defaults_2.update(kwargs)
        review = Review.objects.create(**defaults_2)
        return user, seller, product, order, review

    def test_review_creation(self):
        """Проверяет, что отзыв создаётся с корректными связями и рейтингом."""
        user, seller, _, order, review = self._create_test_service()
        self.assertEqual(review.order, order)
        self.assertEqual(review.author, user)
        self.assertEqual(review.seller, seller)
        self.assertEqual(review.rating, 1)
        self.assertEqual(review.comment, 'ksadh')
        self.assertEqual(Review.objects.count(), 1)

    def test_str_representation(self):
        """Проверяет строковое представление отзыва."""
        _, _, _, _, review = self._create_test_service()
        self.assertEqual(
            str(review), f'Отзыв от {review.author.username} продавцу {review.seller.username}'
        )
