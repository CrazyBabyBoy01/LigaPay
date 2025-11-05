from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from products.forms import (
    AccountServiceFilterForm,
    AccountServiceForm,
    PurchaseForm,
    RPServiceForm,
    ServiceImageForm,
)
from products.models import AccountService, Category, RPService


User = get_user_model()


class AccountServiceFormTestCase(TestCase):
    """
    Тесты для формы AccountServiceForm.
    Проверяют корректность валидации, обязательных полей и соответствие модели.
    """

    def _create_dependencies(self, **kwargs):
        """
        Вспомогательный метод для подготовки зависимостей.
        Создаёт пользователя и категорию, которые понадобятся при тестировании формы.
        Возвращает кортеж (user, category).
        """
        user = User.objects.create_user(
            username='newuser1', email='test1@example.com', password='pass123'
        )
        category = Category.objects.create(name='product5', slug='product_slug4')

        return user, category

    def test_form_valid_with_all_required_fields(self):
        """
        Проверяет, что форма проходит валидацию при корректных данных.
        Ожидается, что is_valid() возвращает True.
        """
        _, category = self._create_dependencies()
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
        form = AccountServiceForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertFalse(form.errors)

    def test_form_invalid_without_required_fields(self):
        """
        Проверяет, что при отсутствии обязательных полей (title, price, server)
        форма становится невалидной и содержит соответствующие ошибки.
        """
        _, category = self._create_dependencies()
        data = {
            'category': str(category.id),
            'quantity': '5',
            'filter_type': 'sell',
            'rank': 'GOLD',
            'account_level': 7,
            'skin_count': 10,
            'character_count': 5,
        }
        form = AccountServiceForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors)

    def test_form_saves_instance_correctly(self):
        """
        Проверяет, что при вызове form.save() создаётся корректный объект AccountService
        с теми же данными, что были переданы в форму.
        """
        user, category = self._create_dependencies()
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
        form = AccountServiceForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertFalse(form.errors)
        instance = form.save(commit=False)
        instance.seller = user
        instance.save()
        self.assertTrue(AccountService.objects.filter(title='Acc1', seller=user).exists())


class RPServiceFormTestCase(TestCase):
    """
    Тесты для формы RPServiceForm.
    Проверяют корректность валидации, обязательных полей и правильность сохранения объекта.
    """

    def _create_dependencies(self):
        """
        Вспомогательный метод для подготовки зависимостей.
        Создаёт пользователя и категорию, которые понадобятся при тестировании формы.
        Возвращает кортеж (user, category).
        """
        user = User.objects.create_user(
            username='newuser1', email='test1@example.com', password='pass123'
        )
        category = Category.objects.create(name='product5', slug='product_slug4')

        return user, category

    def test_form_valid_with_all_required_fields(self):
        """
        Проверяет, что форма проходит валидацию при корректно заполненных данных.
        Ожидается, что form.is_valid() возвращает True, а form.errors пуст.
        """
        _, category = self._create_dependencies()
        data = {
            'title': 'Acc1',
            'price': '100',
            'category': str(category.id),
            'quantity': '5',
            'filter_type': 'gifts_for_rp',
            'server': 'nordic',
        }
        form = RPServiceForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertFalse(form.errors)

    def test_form_invalid_without_required_fields(self):
        """
        Проверяет, что при отсутствии обязательных полей (например title, price, server)
        форма становится невалидной и содержит ошибки в соответствующих полях.
        """
        _, category = self._create_dependencies()
        data = {
            'price': '100',
            'category': str(category.id),
            'quantity': '5',
            'filter_type': 'gifts_for_rp',
            'server': 'nordic',
        }
        form = RPServiceForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors)

    def test_form_saves_instance_correctly(self):
        """
        Проверяет, что при вызове form.save(commit=False) создаётся корректный объект RPService,
        у которого все поля совпадают с переданными в форму, и seller устанавливается вручную.
        После сохранения объект должен существовать в базе данных.
        """
        user, category = self._create_dependencies()
        data = {
            'title': 'Acc1',
            'price': '100',
            'category': str(category.id),
            'quantity': '5',
            'filter_type': 'gifts_for_rp',
            'server': 'nordic',
        }
        form = RPServiceForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertFalse(form.errors)
        instance = form.save(commit=False)
        instance.seller = user
        instance.save()
        self.assertTrue(RPService.objects.filter(title='Acc1', seller=user).exists())


class AccountServiceFilterFormTestCase(TestCase):
    """
    Тесты для формы AccountServiceFilterForm.
    Проверяют корректность валидации полей, применение диапазонов и необязательность фильтров.
    """

    def test_form_valid_with_minimal_data(self):
        """
        Проверяет, что форма проходит валидацию при передаче только минимально необходимых данных.
        Ожидается, что form.is_valid() == True, а form.errors — пустой.
        """
        data = {'server': 'nordic'}
        form = AccountServiceFilterForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertFalse(form.errors)

    def test_form_valid_with_all_filters(self):
        """
        Проверяет, что форма корректно обрабатывает все возможные поля фильтра —
        включая server, rank, числовые диапазоны (account_level_min/max, skin_count_min/max, и т.д.)
        и булевы значения (seller_is_online, is_auto_delivery).
        """
        data = {
            'filter_type': 'sell',
            'rank': 'GOLD',
            'server': 'nordic',
            'is_auto_delivery': True,
            'seller_is_online': True,
            'character_count_min': 1,
            'character_count_max': 10,
            'account_level_min': 1,
            'account_level_max': 10,
            'skin_count_min': 1,
            'skin_count_max': 10,
            'q': 'acc',
        }
        form = AccountServiceFilterForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertFalse(form.errors)

    def test_form_invalid_with_incorrect_data_types(self):
        """
        Проверяет, что при передаче некорректных типов данных (например, строки вместо числа)
        форма становится невалидной и добавляет ошибки в соответствующие поля.
        """
        data = {
            'filter_type': 'sell',
            'rank': 'GOLD',
            'server': 'nordic',
            'is_auto_delivery': True,
            'seller_is_online': True,
            'character_count_min': 1,
            'character_count_max': 10,
            'account_level_min': 1,
            'account_level_max': 'asdas',
            'skin_count_min': 1,
            'skin_count_max': 10,
            'q': 'acc',
        }
        form = AccountServiceFilterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors)

    def test_form_fields_are_optional(self):
        """
        Проверяет, что все поля формы не обязательны, то есть форма должна быть валидна
        даже при полностью пустом вводе (form.is_valid() == True).
        """
        data = {
            'filter_type': '',
            'rank': '',
            'server': '',
            'q': '',
        }
        form = AccountServiceFilterForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertFalse(form.errors)


class ServiceImageFormTestCase(TestCase):
    """
    Тесты для формы ServiceImageForm.
    Проверяют корректность валидации поля image при передаче валидного файла,
    при передаче не-изображения, а также поведение при отсутствии файла (required=False).
    """

    def _generate_test_image(self):
        """
        Создаёт простое изображение 1x1 пиксель в памяти
        и возвращает его как SimpleUploadedFile.
        """
        image = Image.new('RGB', (1, 1), color='white')
        buffer = BytesIO()
        image.save(buffer, format='JPEG')
        return SimpleUploadedFile('test.jpg', buffer.getvalue(), content_type='image/jpeg')

    def test_form_valid_with_correct_image(self):
        """
        Проверяет, что форма проходит валидацию при передаче корректного изображения.
        Ожидается, что form.is_valid() == True и ошибок нет.
        """
        image = self._generate_test_image()
        form = ServiceImageForm(data={}, files={'image': image})
        self.assertTrue(form.is_valid())

    def test_form_invalid_with_non_image_file(self):
        """
        Проверяет, что форма становится невалидной при передаче файла,
        который не является изображением (например, текстового файла).
        """
        broken_file = SimpleUploadedFile('test.txt', b'not an image', content_type='text/plain')
        form = ServiceImageForm(data={}, files={'image': broken_file})
        self.assertFalse(form.is_valid())
        self.assertIn('image', form.errors)

    def test_form_valid_without_file_when_not_required(self):
        """
        Проверяет, что форма остаётся валидной при отсутствии изображения,
        так как поле image имеет required=False.
        """
        form = ServiceImageForm(data={}, files={})
        self.assertTrue(form.is_valid())
        self.assertFalse(form.errors)


class PurchaseFormTestCase(TestCase):
    """
    Тесты для формы PurchaseForm.
    Проверяют обязательные поля, корректность типов данных и допустимость пустых необязательных полей.
    """

    def test_form_valid_with_required_fields_only(self):
        """
        Проверяет, что форма валидна при заполнении только обязательных полей:
        payment_method и player_id. Поля amount и price могут быть пустыми.
        Ожидается: is_valid() == True, ошибок нет.
        """
        data = {
            'payment_method': 'method1',
            'player_id': 'фыв',
            'amount': '',
            'price': '',
        }
        form = PurchaseForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertFalse(form.errors)

    def test_form_invalid_without_payment_method(self):
        """
        Проверяет, что отсутствие payment_method делает форму невалидной.
        Ожидается: is_valid() == False, ошибка в поле 'payment_method'.
        """
        data = {
            'player_id': 'фыв',
            'amount': '',
            'price': '',
        }
        form = PurchaseForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors)

    def test_form_invalid_without_player_id(self):
        """
        Проверяет, что отсутствие player_id делает форму невалидной.
        Ожидается: is_valid() == False, ошибка в поле 'player_id'.
        """
        data = {
            'payment_method': 'method1',
            'amount': '',
            'price': '',
        }
        form = PurchaseForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors)

    def test_form_invalid_with_unknown_payment_method(self):
        """
        Проверяет, что неверное значение для ChoiceField (payment_method)
        приводит к ошибке валидации.
        Ожидается: is_valid() == False, ошибка в поле 'payment_method'.
        """
        data = {
            'payment_method': 'ыфв',
            'player_id': 'фыв',
            'amount': '',
            'price': '',
        }
        form = PurchaseForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors)

