from io import BytesIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from chat.models import ChatRoom
from products.forms import AccountServiceFilterForm, AccountServiceForm, RPServiceForm
from products.models import AccountService, Category, RPService, ServiceImage


User = get_user_model()
TWO_WEEKS = 1209600


class BaseTestUtils(TestCase):
    def _generate_test_image(self):
        """
        Создаёт простое изображение 1x1 пиксель в памяти и возвращает его как SimpleUploadedFile.
        """
        image = Image.new('RGB', (1, 1), color='white')
        buffer = BytesIO()
        image.save(buffer, format='JPEG')
        return SimpleUploadedFile('test.jpg', buffer.getvalue(), content_type='image/jpeg')

    def _create_test_service(self, model=RPService, **kwargs):
        """
        Вспомогательный метод для создания тестового объекта.

        Создаёт пользователя, категорию и услугу с базовыми корректными данными.
        При необходимости можно передать дополнительные параметры через **kwargs
        для переопределения стандартных значений.
        Возвращает созданный объект.
        """
        user = User.objects.create_user(
            username='newuser1', email='test1@example.com', password='pass123'
        )
        category = Category.objects.create(name='product5', slug='product_slug4')
        product = model.objects.create(
            title='Rp', seller=user, price=100, category=category, quantity=5, **kwargs
        )
        return user, category, product


class CategoryViewTestCase(TestCase):
    def test_category_view_returns_category_with_valid_slug(self):
        """Проверяет, что при корректном slug view возвращает страницу категории (200)."""
        Category.objects.create(name='Account', description='text', slug='accounts')
        url = reverse('products:category', kwargs={'slug': 'accounts'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/products.html')
        self.assertIn('title', response.context)
        self.assertEqual(response.context['title'], 'Услуги')

    def test_category_view_returns_404_with_invalid_slug(self):
        """Проверяет, что при несуществующем slug возвращается 404."""
        Category.objects.create(name='Account', description='text', slug='accounts')
        url = reverse('products:category', kwargs={'slug': 'acc'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateNotUsed(response, 'products/products.html')


class BaseServiceDetailViewTestCase(BaseTestUtils):
    """Тесты для представления BaseServiceDetailView."""

    def test_detail_view_returns_correct_object(self):
        """Проверяет, что при корректном ID view возвращает правильный объект и статус 200."""
        _, _, product = self._create_test_service()
        url = reverse('products:riot-points_detail', kwargs={'pk': product.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('service', response.context)
        self.assertEqual(response.context['service'].id, product.id)

    def test_detail_view_returns_404_for_nonexistent_object(self):
        """Проверяет, что при несуществующем ID view возвращает страницу 404."""
        _, _, product = self._create_test_service()
        url = reverse('products:riot-points_detail', kwargs={'pk': product.id + 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_context_contains_expected_keys(self):
        """
        Проверяет, что контекст содержит все ожидаемые ключи (form, form_purchase, is_buyermodel_name).
        """
        _, _, product = self._create_test_service()
        url = reverse('products:riot-points_detail', kwargs={'pk': product.id})
        response = self.client.get(url)
        self.assertIn('form', response.context)
        self.assertIn('form_purchase', response.context)
        self.assertIn('is_buyer', response.context)
        self.assertIn('model_name', response.context)
        self.assertIsInstance(response.context['form'], RPServiceForm)

    def test_is_buyer_is_true_for_different_user(self):
        """Проверяет, что is_buyer=True, если пользователь не является продавцом."""
        _, _, product = self._create_test_service()
        buyer = User.objects.create_user(username='buyer', password='pass123')
        self.client.force_login(buyer)
        url = reverse('products:riot-points_detail', kwargs={'pk': product.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('is_buyer', response.context)
        self.assertEqual(response.context['is_buyer'], True)

    def test_is_buyer_is_false_for_seller(self):
        """Проверяет, что is_buyer=False, если пользователь сам является продавцом."""
        # Логика: выполнить GET-запрос от имени продавца и проверить значение is_buyer
        user, _, product = self._create_test_service()
        self.client.force_login(user)
        url = reverse('products:riot-points_detail', kwargs={'pk': product.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['is_buyer'], False)

    def test_post_returns_403_for_unauthenticated_user(self):
        """Проверяет, что неавторизованный пользователь получает 403 при попытке удалить сервис."""
        _, _, product = self._create_test_service()
        url = reverse('products:riot-points_detail', kwargs={'pk': product.id})
        response = self.client.post(url, {'delete': ''})
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data['success'], False)
        self.assertIn('нет прав', data['message'])

    def test_post_returns_403_for_not_owner_user(self):
        """Проверяет, что авторизованный пользователь, не являющийся продавцом, получает 403."""
        _, _, product = self._create_test_service()
        buyer = User.objects.create_user(username='buyer', password='pass123')
        self.client.force_login(buyer)
        url = reverse('products:riot-points_detail', kwargs={'pk': product.id})
        response = self.client.post(url, {'delete': ''})
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data['success'], False)
        self.assertIn('нет прав', data['message'])

    def test_post_allows_owner_to_delete_service(self):
        """Проверяет, что продавец может успешно удалить свой сервис (редирект на my_products)."""
        user, _, product = self._create_test_service()
        self.client.force_login(user)
        url = reverse('products:riot-points_detail', kwargs={'pk': product.id})
        response = self.client.post(url, {'delete': ''})
        self.client.post(url, {'delete': ''})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(RPService.objects.filter(pk=product.pk).exists())

    def test_edit_service_with_valid_data_updates_object(self):
        """Проверяет, что продавец может успешно обновить данные услуги (валидная форма)."""
        user, _, product = self._create_test_service()
        self.client.force_login(user)
        url = reverse('products:riot-points_detail', kwargs={'pk': product.id})
        response = self.client.post(
            url,
            {
                'edit_service': '',
                'title': 'Rp1',
                'price': 200,
                'quantity': 4,
                'filter_type': 'gifts_for_rp',
                'server': 'nordic',
            },
        )
        expected_url = reverse('products:riot-points_detail', kwargs={'pk': product.pk})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(RPService.objects.filter(title='Rp1').exists())
        self.assertRedirects(response, expected_url)

    def test_edit_service_with_invalid_data_rerenders_form(self):
        """Проверяет, что при невалидных данных форма отображается снова с ошибками."""
        user, _, product = self._create_test_service()
        self.client.force_login(user)
        url = reverse('products:riot-points_detail', kwargs={'pk': product.id})
        response = self.client.post(
            url,
            {
                'edit_service': '',
                'title': 'Rp1',
                'price': 200,
                'quantity': 4,
                'filter_type': 'gifts_for_rp',
                'server': '',
            },
        )
        form = response.context['form']
        product.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(RPService.objects.filter(title='Rp').exists())
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors)
        self.assertIn('server', form.errors)

    def test_add_image_with_valid_file_creates_image(self):
        """Проверяет, что при валидном файле изображение успешно добавляется и сохраняется в базе."""
        user, category, _ = self._create_test_service(AccountService)
        product = AccountService.objects.create(
            title='Acc',
            seller=user,
            price=100,
            category=category,
            quantity=5,
        )
        self.client.force_login(user)
        url = reverse('products:accounts_detail', kwargs={'pk': product.id})
        test_image = self._generate_test_image()
        response = self.client.post(url, {'add_image': '', 'image': test_image})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['success'], True)
        self.assertEqual(ServiceImage.objects.count(), 1)

    def test_add_image_without_file_returns_error(self):
        """Проверяет, что при отсутствии файла метод возвращает ошибку и success=False."""
        user, category, _ = self._create_test_service(AccountService)
        product = AccountService.objects.create(
            title='Acc',
            seller=user,
            price=100,
            category=category,
            quantity=5,
        )
        broken_file = SimpleUploadedFile(
            'broken.jpg',
            b'this is not an image',
            content_type='image/jpeg',
        )
        self.client.force_login(user)
        url = reverse('products:accounts_detail', kwargs={'pk': product.id})
        response = self.client.post(url, {'add_image': '', 'image': broken_file})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['success'], False)
        self.assertIn('Ошибка при загрузке изображения.', data['message'])
        self.assertEqual(ServiceImage.objects.count(), 0)

    def test_add_image_limit_exceeded_returns_error(self):
        """
        Проверяет, что при попытке добавить более 4 изображений возвращается сообщение об ограничении.
        """
        user, category, _ = self._create_test_service(AccountService)
        product = AccountService.objects.create(
            title='Acc',
            seller=user,
            price=100,
            category=category,
            quantity=5,
        )
        content_type = ContentType.objects.get_for_model(product)
        for _ in range(4):
            ServiceImage.objects.create(
                content_type=content_type,
                object_id=product.id,
                image=self._generate_test_image(),
            )
        self.client.force_login(user)
        url = reverse('products:accounts_detail', kwargs={'pk': product.id})
        test_image = self._generate_test_image()
        response = self.client.post(url, {'add_image': '', 'image': test_image})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['success'], False)
        self.assertIn('Максимум 4 изображения разрешено.', data['message'])
        self.assertEqual(ServiceImage.objects.count(), 4)

    def test_delete_image_removes_existing_image(self):
        """
        Проверяет, что при передаче корректного ID изображение успешно удаляется
        и в ответе возвращается success=True.
        """
        user, category, _ = self._create_test_service(AccountService)
        product = AccountService.objects.create(
            title='Acc',
            seller=user,
            price=100,
            category=category,
            quantity=5,
        )
        content_type = ContentType.objects.get_for_model(product)
        img = ServiceImage.objects.create(
            content_type=content_type,
            object_id=product.id,
            image=self._generate_test_image(),
        )
        self.client.force_login(user)
        url = reverse('products:accounts_detail', kwargs={'pk': product.id})
        response = self.client.post(url, {'delete_image': '', 'image_id': img.id})
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(ServiceImage.objects.count(), 0)

    def test_delete_image_returns_false_for_nonexistent_id(self):
        """
        Проверяет, что при попытке удалить несуществующее изображение
        возвращается success=False и сообщение об ошибке.
        """
        user, category, _ = self._create_test_service(AccountService)
        product = AccountService.objects.create(
            title='Acc',
            seller=user,
            price=100,
            category=category,
            quantity=5,
        )
        self.client.force_login(user)
        url = reverse('products:accounts_detail', kwargs={'pk': product.id})
        response = self.client.post(url, {'delete_image': '', 'image_id': 999})
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], False)
        self.assertIn('Ошибка при удалении изображения.', data['message'])

    def test_delete_image_denied_for_not_owner(self):
        """
        Проверяет, что пользователь не может удалить изображение,
        принадлежащее чужому сервису (ответ — 403 или success=False).
        """

        user, category, _ = self._create_test_service(AccountService)
        product = AccountService.objects.create(
            title='Acc',
            seller=user,
            price=100,
            category=category,
            quantity=5,
        )
        content_type = ContentType.objects.get_for_model(product)
        img = ServiceImage.objects.create(
            content_type=content_type,
            object_id=product.id,
            image=self._generate_test_image(),
        )
        buyer = User.objects.create_user(username='buyer', password='pass123')
        self.client.force_login(buyer)
        url = reverse('products:accounts_detail', kwargs={'pk': product.id})
        response = self.client.post(url, {'delete_image': '', 'image_id': img.id})
        data = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertIn('У вас нет прав на это действие.', data['message'])


class BaseServiceListViewTestCase(BaseTestUtils):
    """Тесты для представления BaseServiceListView."""

    def test_get_queryset_excludes_services_of_authenticated_user(self):
        """
        Проверяет, что при авторизованном пользователе его собственные услуги не попадают в выдачу."""
        user, category, _ = self._create_test_service(AccountService)
        products = []
        for i in range(2):
            product = AccountService.objects.create(
                title=f'Product {i+1}', seller=user, category=category, price=100 + i * 10, quantity=5
            )
            products.append(product)
        user_2 = User.objects.create_user(
            username='newuser2', email='test2@example.com', password='pass123'
        )
        AccountService.objects.create(
            title='Acc1', seller=user_2, price=100, category=category, quantity=5
        )
        self.client.force_login(user_2)
        url = reverse('products:account')
        ChatRoom.objects.create(is_global=True)
        response = self.client.get(url)
        services = list(response.context['services'])
        self.assertTrue(all(s.seller != user_2 for s in services))

    def test_get_queryset_includes_all_active_services_for_guest(self):
        """
        Проверяет, что неавторизованный пользователь видит все активные услуги.
        """
        user, category, _ = self._create_test_service(AccountService)
        products = []
        for i in range(1):
            product = AccountService.objects.create(
                title=f'Product {i+1}', seller=user, category=category, price=100 + i * 10, quantity=5
            )
            products.append(product)
        self.client.logout()
        user_2 = User.objects.create_user(
            username='newuser3', email='test3@example.com', password='pass123'
        )
        AccountService.objects.create(
            title='Acc1', seller=user_2, price=100, category=category, quantity=5
        )
        url = reverse('products:account')
        ChatRoom.objects.create(is_global=True)
        response = self.client.get(url)
        services = list(response.context['services'])
        sellers = {s.seller for s in services}

        self.assertIn(user, sellers)
        self.assertIn(user_2, sellers)
        self.assertEqual(len(services), AccountService.objects.count())

    def test_post_returns_403_for_unauthenticated_user(self):
        """
        Проверяет, что неавторизованный пользователь не может создать новую услугу (403 Forbidden).
        """
        Category.objects.create(name='product5', slug='product_slug4')
        ChatRoom.objects.create(is_global=True)
        url = reverse('products:account')
        data = {
            'title': 'Acc1',
            'price': '100',
            'category': 'category',
            'quantity': '5',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(AccountService.objects.count(), 0)

    def test_post_creates_service_for_authenticated_user(self):
        """
        Проверяет, что при валидной форме создаётся новая услуга и назначается текущий
        пользователь как продавец.
        """
        user, category, _ = self._create_test_service(AccountService)
        ChatRoom.objects.create(is_global=True)
        self.client.force_login(user)
        url = reverse('products:account')

        data = {
            'title': 'Acc1',
            'price': '100',
            'category': str(category.id),
            'quantity': '5',
            'filter_type': 'sell',
            'rank': 'GOLD',
            'server': 'nordic',
            'account_level': 7,
            'skin_count': 10,
            'character_count': 5,
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(AccountService.objects.filter(title='Acc1', seller=user).exists())

    def test_post_with_invalid_data_rerenders_page_and_logs_error(self):
        """
        Проверяет, что при невалидных данных форма не сохраняется, ошибки логируются и
        возвращается статус 200.
        """
        user, category, _ = self._create_test_service(AccountService)
        ChatRoom.objects.create(is_global=True)
        self.client.force_login(user)
        url = reverse('products:account')

        data = {
            'title': 'Acc1',
            'price': '100',
            'category': str(category.id),
            'quantity': '5',
            'filter_type': 'sell',
            'server': 'nordic',
            'account_level': 7,
            'skin_count': 10,
            'character_count': 5,
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(AccountService.objects.count(), 1)
        form = response.context['form']
        self.assertFalse(form.is_valid())

    def test_post_creates_service_with_image_if_valid(self):
        """
        Проверяет, что при валидном изображении создаётся услуга и к ней привязывается изображение.
        """
        user, category, _ = self._create_test_service(AccountService)
        ChatRoom.objects.create(is_global=True)
        self.client.force_login(user)
        test_image = self._generate_test_image()
        data = {
            'title': 'Acc123',
            'price': '100',
            'category': str(category.id),
            'quantity': '5',
            'filter_type': 'sell',
            'rank': 'PLATINUM',
            'server': 'nordic',
            'account_level': 7,
            'skin_count': 10,
            'character_count': 5,
            'image': test_image,
        }
        url = reverse('products:account')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(AccountService.objects.count(), 2)
        self.assertEqual(ServiceImage.objects.count(), 1)

    def test_post_does_not_save_image_if_form_invalid(self):
        """
        Проверяет, что если форма услуги невалидна, изображение не сохраняется в базу.
        """
        user, category, _ = self._create_test_service(AccountService)
        ChatRoom.objects.create(is_global=True)
        self.client.force_login(user)
        test_image = self._generate_test_image()
        data = {
            'title': 'Acc123',
            'price': '100',
            'category': str(category.id),
            'quantity': '5',
            'filter_type': 'sell',
            'rank': 'PLATINUM',
            'server': 'nordic',
            'account_level': 7,
            'character_count': 5,
            'image': test_image,
        }
        url = reverse('products:account')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(AccountService.objects.count(), 1)
        self.assertEqual(ServiceImage.objects.count(), 0)

    def test_get_queryset_applies_filter_when_filter_form_valid(self, **kwargs):
        """
        Проверяет, что если форма фильтрации валидна, queryset фильтруется согласно переданным данным."""
        user, category, _ = self._create_test_service(AccountService)
        AccountService.objects.create(
            title='Acc3', seller=user, price=100, category=category, rank='GOLD', quantity=5, **kwargs
        )
        ChatRoom.objects.create(is_global=True)
        url = reverse('products:account')
        response = self.client.get(url, {'rank': 'GOLD'})
        services = list(response.context['services'])
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(s.rank == 'GOLD' for s in services))
        self.assertEqual(len(services), 1)
        self.assertTemplateUsed(response, 'products/account.html')

    def test_get_context_contains_filter_and_create_forms(self, **kwargs):
        """
        Проверяет, что контекст шаблона содержит обе формы: фильтра и создания услуги.
        """
        user, category, _ = self._create_test_service(AccountService)
        AccountService.objects.create(
            title='Acc3', seller=user, price=100, category=category, rank='GOLD', quantity=5, **kwargs
        )
        ChatRoom.objects.create(is_global=True)
        url = reverse('products:account')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('filter_form', response.context)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['filter_form'], AccountServiceFilterForm)
        self.assertIsInstance(response.context['form'], AccountServiceForm)
        self.assertTemplateUsed(response, 'products/account.html')

    def test_get_queryset_ignores_filter_when_form_invalid(self, **kwargs):
        """
        Проверяет, что при невалидной форме фильтрации queryset остаётся неизменным
        (все активные услуги).
        """
        user, category, _ = self._create_test_service(AccountService)
        AccountService.objects.create(
            title='Acc3', seller=user, price=100, category=category, rank='GOLD', quantity=5, **kwargs
        )
        ChatRoom.objects.create(is_global=True)
        url = reverse('products:account')
        response = self.client.get(url, {'rank': 'вжыфдл'})
        services = list(response.context['services'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(services), 2)
        self.assertTemplateUsed(response, 'products/account.html')

    def test_post_with_file_upload_saves_image_with_correct_relation(self):
        """
        Проверяет, что при отправке файла изображение связывается с правильным объектом
        через GenericForeignKey.
        """
        user, category, _ = self._create_test_service(AccountService)
        ChatRoom.objects.create(is_global=True)
        self.client.force_login(user)
        test_image = self._generate_test_image()
        data = {
            'title': 'Acc123',
            'price': '100',
            'category': str(category.id),
            'quantity': '5',
            'filter_type': 'sell',
            'rank': 'PLATINUM',
            'server': 'nordic',
            'account_level': 7,
            'skin_count': 10,
            'character_count': 5,
            'image': test_image,
        }
        url = reverse('products:account')
        response = self.client.post(url, data)
        service = AccountService.objects.last()
        image = ServiceImage.objects.first()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(AccountService.objects.count(), 2)
        self.assertEqual(ServiceImage.objects.count(), 1)
        self.assertEqual(image.content_type.model, 'accountservice')
        self.assertEqual(image.object_id, service.id)
        self.assertEqual(image.content_object, service)

    def test_post_creates_service_returns_redirect_to_same_page(self):
        """
        Проверяет, что после успешного создания услуги происходит редирект на текущий путь.
        """
        user, category, _ = self._create_test_service(AccountService)
        ChatRoom.objects.create(is_global=True)
        self.client.force_login(user)
        url = reverse('products:account')
        data = {
            'title': 'Acc123',
            'price': '100',
            'category': str(category.id),
            'quantity': '5',
            'filter_type': 'sell',
            'rank': 'PLATINUM',
            'server': 'nordic',
            'account_level': 7,
            'skin_count': 10,
            'character_count': 5,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, url)
        self.assertTrue(AccountService.objects.filter(title='Acc123', seller=user).exists())

    @patch('products.views.logger')
    def test_logger_error_called_when_form_invalid(self, mock_logger):
        """
        Проверяет, что при невалидной форме вызывается logger.error с описанием ошибок.
        """
        user, category, _ = self._create_test_service(AccountService)
        ChatRoom.objects.create(is_global=True)
        self.client.force_login(user)
        url = reverse('products:account')
        data = {
            'title': 'Acc123',
            'price': '100',
            'category': str(category.id),
            'filter_type': 'sell',
            'rank': 'PLATINUM',
            'server': 'nordic',
            'account_level': 7,
            'skin_count': 10,
            'character_count': 5,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        mock_logger.error.assert_called_once()
        self.assertIn('Ошибка в форме', mock_logger.error.call_args[0][0])
        self.assertFalse(AccountService.objects.filter(title='Acc123', seller=user).exists())
