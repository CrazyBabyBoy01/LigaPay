import time
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from products.models import AccountService, Category, RPService, ServiceImage


User = get_user_model()


class CategoryModelTest(TestCase):
    def test_create_category_success(self):
        """Тест успешного создания категории с корректными данными"""
        category = Category.objects.create(name='product', description='text', slug='product_slug')
        category_from_db = Category.objects.get(name='product')
        self.assertEqual(category.name, 'product')
        self.assertEqual(category.description, 'text')
        self.assertEqual(category.slug, 'product_slug')
        self.assertEqual(Category.objects.count(), 1)
        self.assertTrue(isinstance(category, Category))
        self.assertEqual(category_from_db.slug, 'product_slug')

    def test_create_category_without_description(self):
        """Тест создания категории без поля description (оно необязательное)"""
        category = Category.objects.create(name='product1', slug='product_slug1')
        self.assertEqual(category.description, '')

    def test_category_str_method(self):
        """Тест строкового представления модели (должно возвращать name)"""
        category = Category.objects.create(name='product2', description='text', slug='product_slug2')
        self.assertEqual(str(category), category.name)

    def test_unique_name_constraint(self):
        """Тест ошибки при создании категории с одинаковым name"""
        Category.objects.create(name='product10', slug='product_slug3')
        with self.assertRaises(IntegrityError), transaction.atomic():
            Category.objects.create(name='product10', slug='product_slug4')
        self.assertEqual(Category.objects.count(), 1)

    def test_unique_slug_constraint(self):
        """Тест ошибки при создании категории с одинаковым slug"""
        Category.objects.create(name='product4', slug='product_slug4')
        with self.assertRaises(IntegrityError), transaction.atomic():
            Category.objects.create(name='product5', slug='product_slug4')
        self.assertEqual(Category.objects.count(), 1)


class BaseServiceModelTest(TestCase):
    """
    Тесты для базовой модели BaseService (проверяются через потомка).
    """

    def _create_rp_service(self, **kwargs):
        """
        Вспомогательный метод для создания тестового объекта RPService.

        Создаёт пользователя, категорию и услугу с базовыми корректными данными.
        При необходимости можно передать дополнительные параметры через **kwargs
        для переопределения стандартных значений.
        Возвращает созданный объект RPService.
        """
        user = User.objects.create_user(
            username='newuser1', email='test1@example.com', password='pass123'
        )
        category = Category.objects.create(name='product5', slug='product_slug4')
        product = RPService.objects.create(
            title='Rp', seller=user, price=100, category=category, quantity=5, **kwargs
        )
        return user, category, product

    def test_create_service_success(self):
        """Тест успешного создания услуги с корректными данными"""

        user, category, product = self._create_rp_service()
        self.assertEqual(product.title, 'Rp')
        self.assertEqual(product.seller, user)
        self.assertEqual(product.price, Decimal('100.00'))
        self.assertEqual(product.quantity, 5)
        self.assertEqual(product.is_auto_delivery, False)
        self.assertEqual(product.seller_is_online, False)
        self.assertEqual(RPService.objects.count(), 1)
        self.assertEqual(product.category, category)
        self.assertTrue(isinstance(category, Category))
        self.assertTrue(isinstance(product, RPService))

    def test_service_str_method(self):
        """
        Тест строкового представления услуги BaseService.__str__ не тестируется напрямую,
        а поведение проверяется через наследников
        """
        _, _, product = self._create_rp_service()
        self.assertEqual(
            str(product), f'{product.title} - {product.server} - {product.quantity} доступно'
        )

    def test_service_update_timestamp(self):
        """Тест автоматического обновления поля updated_at при изменении объекта"""
        _, _, product = self._create_rp_service()
        old_updated_at = product.updated_at
        product.price = Decimal('150.00')
        time.sleep(1)
        product.save()
        product.refresh_from_db()
        new_updated_at = product.updated_at
        self.assertGreater(new_updated_at, old_updated_at)


class ServiceImageModelTest(TestCase):
    """
    Тесты для модели ServiceImage.
    """

    def _create_account_service_with_image(self, **kwargs):
        """
        Вспомогательный метод для создания тестового объекта AccountService
        вместе с изображением ServiceImage.
        Возвращает кортеж (service, image).
        """
        user = User.objects.create_user(
            username='newuser1', email='test1@example.com', password='pass123'
        )
        category = Category.objects.create(name='product5', slug='product_slug4')
        product = AccountService.objects.create(
            title='Acc', seller=user, price=100, category=category, quantity=5, **kwargs
        )
        img = ServiceImage.objects.create(content_object=product, image='path.jpg')
        return product, img

    def test_service_image_str_method(self):
        _, img = self._create_account_service_with_image()

        self.assertEqual(str(img), f'Image for {img.content_object}')

    def test_service_image_deleted_with_related_object(self):
        """Тест, что изображение удаляется при удалении связанного объекта"""
        product, _ = self._create_account_service_with_image()

        self.assertEqual(ServiceImage.objects.count(), 1)
        product.delete()
        self.assertEqual(ServiceImage.objects.count(), 0)
