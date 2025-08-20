from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now, timedelta

from .models import User


class UserModelTests(TestCase):
    # Проверяем создание обычного пользователя
    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser', email='test@example.com', password='pass1234'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertFalse(user.is_verified_email)
        self.assertFalse(user.is_online())

    # Проверяем создание суперпользователя
    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='admin123'
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    # Проверяем метод is_online для пользователя с последней активностью сейчас
    def test_is_online_true(self):
        user = User.objects.create_user(
            username='onlineuser', email='online@example.com', password='pass1234'
        )
        user.last_activity = now()
        user.save()
        self.assertTrue(user.is_online())

    # Проверяем метод is_online для пользователя, который был активен давно
    def test_is_online_false(self):
        user = User.objects.create_user(
            username='offlineuser', email='offline@example.com', password='pass1234'
        )
        user.last_activity = now() - timedelta(minutes=10)
        user.save()
        self.assertFalse(user.is_online())


class UserRegistrationViewTests(TestCase):
    # Проверяем, что страница регистрации доступна и рендерится с нужным шаблоном
    def test_registration_page_loads(self):
        url = reverse('users:registration')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/registration.html')

    # Проверяем успешную регистрацию пользователя
    @patch('captcha.fields.CaptchaField.clean', return_value='PASSED')
    def test_user_registration_success(self, mock_captcha):
        url = reverse('users:registration')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'captcha_0': 'dummy',
            'captcha_1': 'PASSED',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    # Проверяем регистрацию с несовпадающими паролями
    @patch('captcha.fields.CaptchaField.clean', return_value='PASSED')
    def test_user_registration_password_mismatch(self, mock_captcha):
        url = reverse('users:registration')
        data = {
            'username': 'newuser2',
            'email': 'newuser2@example.com',
            'password1': 'password123',
            'password2': 'different123',
            'captcha_0': 'dummy',
            'captcha_1': 'PASSED',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(User.objects.filter(username='newuser2').exists())
        self.assertFormError(form, 'password2', 'Введенные пароли не совпадают.')

    # Проверяем регистрацию с уже существующим email
    @patch('captcha.fields.CaptchaField.clean', return_value='PASSED')
    def test_user_registration_duplicate_email(self, mock_captcha):
        User.objects.create_user(username='existuser', email='exist@example.com', password='pass1234')
        url = reverse('users:registration')
        data = {
            'username': 'newuser3',
            'email': 'exist@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'captcha_0': 'dummy',
            'captcha_1': 'PASSED',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(User.objects.filter(username='newuser3').exists())
        self.assertFormError(form, 'email', 'Пользователь с таким Email уже существует.')


class UserAuthenticationTests(TestCase):
    # Создаем пользователя, который будет использоваться в тестах
    def setUp(self):
        self.user = User.objects.create_user(username='loginuser', password='pass1234')

    # Проверяем успешный вход пользователя с правильными учетными данными
    def test_login_success(self):
        login = self.client.login(username='loginuser', password='pass1234')
        self.assertTrue(login)

    # Проверяем, что вход с неправильным паролем не проходит
    def test_login_fail(self):
        login = self.client.login(username='loginuser', password='wrongpass')
        self.assertFalse(login)

    # Проверяем корректный выход пользователя (logout)
    def test_logout(self):
        self.client.login(username='loginuser', password='pass1234')
        response = self.client.get(reverse('users:logout'))
        self.assertEqual(response.status_code, 302)  # редирект после логаута
