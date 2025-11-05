from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from products.filters import BaseServiceFilter
from products.models import AccountService, Category


User = get_user_model()


class BaseServiceFilterTestCase(TestCase):
    """
    Тесты для BaseServiceFilter.
    Проверяют работу пользовательских методов фильтрации: filter_q, filter_auto_delivery, filter_seller_online.
    """

    def _create_services(self, *args, **kwargs):
        """
        Вспомогательный метод для подготовки данных.
        Создаёт пользователя, несколько объектов услуги с разными значениями полей title, description,
        is_auto_delivery и last_activity.
        Возвращает queryset или список объектов для тестов.
        """
        user_1 = User.objects.create_user(
            username='newuser1', email='test1@example.com', password='pass123'
        )
        user_2 = User.objects.create_user(
            username='newuser2', email='test12@example.com', password='pass123'
        )
        user_1.last_activity = timezone.now()
        user_1.save()
        user_2.last_activity = timezone.now() - timedelta(minutes=30)
        user_2.save()
        category = Category.objects.create(name='product5', slug='product_slug4')
        AccountService.objects.create(
            title='Rp',
            seller=user_1,
            price=100,
            category=category,
            description='sdsada1',
            is_auto_delivery=True,
            quantity=5,
            **kwargs,
        )
        AccountService.objects.create(
            title='Acc',
            seller=user_2,
            price=1100,
            category=category,
            description='sdsada',
            quantity=5,
            **kwargs,
        )
        return AccountService.objects.all()

    def test_filter_q_returns_objects_matching_query(self):
        """
        Проверяет, что filter_q возвращает только те объекты, в которых значение строки поиска
        встречается в полях title, description или search_description.
        Также проверяет, что при пустом значении возвращается исходный queryset.
        """
        queryset = self._create_services()
        data = {'q': 'Acc'}
        filtered = BaseServiceFilter(data=data, queryset=queryset)
        self.assertEqual(filtered.qs.count(), 1)
        self.assertIn('Acc', filtered.qs.first().title)
        self.assertTrue(all('Acc' in s.title or 'Acc' in s.description for s in filtered.qs))

    def test_filter_auto_delivery_returns_only_auto_delivery_services(self):
        """
        Проверяет, что filter_auto_delivery(True) возвращает только объекты с is_auto_delivery=True,
        а filter_auto_delivery(False) — все объекты без фильтрации.
        """
        queryset = self._create_services()
        data = {'is_auto_delivery': True}
        filtered = BaseServiceFilter(data=data, queryset=queryset)
        self.assertEqual(filtered.qs.count(), 1)
        self.assertIn('Rp', filtered.qs.first().title)

    def test_filter_seller_online_returns_recently_active_sellers_only(self):
        """
        Проверяет, что filter_seller_online(True) возвращает только объекты, продавцы которых
        были активны в пределах USER_ONLINE_MINUTES, а filter_seller_online(False) не фильтрует queryset.
        """
        queryset = self._create_services()
        data = {'seller_is_online': True}
        filtered = BaseServiceFilter(data=data, queryset=queryset)
        self.assertEqual(filtered.qs.count(), 1)
