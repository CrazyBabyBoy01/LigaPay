import uuid
from datetime import timedelta
from unittest.mock import ANY, Mock, patch

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode

from users.models import EmailVerification
from users.views import ChangeEmailView


User = get_user_model()
code = uuid.uuid4()
TWO_WEEKS = 1209600


class UserLoginViewTestCase(TestCase):
    def create_user(self, username='testuser'):
        """Создание пользователя"""
        return User.objects.create_user(username=username, email='test@example.com', password='pass1234')

    def test_form_valid_remember_me_true(self):
        """Проверяет, что при remember_me=True сессия сохраняется на 2 недели"""
        user = self.create_user(username='testuser1')  # noqa: F841
        url = reverse('users:authorization')
        data = {'username': 'testuser1', 'password': 'pass1234', 'remember_me': True}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertFalse(self.client.session.get_expire_at_browser_close())
        self.assertEqual(self.client.session.get_expiry_age(), TWO_WEEKS)

    def test_form_valid_remember_me_false(self):
        """Проверяет, что при remember_me=False сессия завершается при закрытии браузера"""
        user = self.create_user(username='testuser2')  # noqa: F841
        url = reverse('users:authorization')
        data = {
            'username': 'testuser2',
            'password': 'pass1234',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertTrue(self.client.session.get_expire_at_browser_close())


class UserRegistrationViewTestCase(TestCase):
    @patch('captcha.fields.CaptchaField.clean', return_value='PASSED')
    def test_user_registration_succes(self, mock_captcha):
        """
        Проверяет успешную регистрацию пользователя:
        - форма проходит валидацию (включая капчу);
        - создаётся новый объект User;
        - пользователь перенаправляется (302);
        - email ещё не подтверждён (is_verified_email=False).
        """
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
        user = User.objects.get(username='newuser')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser', email='newuser@example.com').exists())
        self.assertFalse(user.is_verified_email)

    @patch('captcha.fields.CaptchaField.clean', return_value='PASSED')
    def test_registration_with_existing_email(self, mock_captcha):
        """Форма невалидна при повторной регистрации с тем же email"""
        User.objects.create_user(username='newuser1', email='test@example.com', password='pass123')
        url = reverse('users:registration')
        data = {
            'username': 'newuser',
            'email': 'test@example.com',
            'password1': 'pass1234',
            'password2': 'pass1234',
            'captcha_0': 'dummy',
            'captcha_1': 'PASSED',
        }
        response = self.client.post(url, data)
        form = response.context['form']
        self.assertEqual(response.status_code, 200)
        self.assertFormError(form, 'email', 'Пользователь с таким Почта уже существует.')


class EmailVerificationViewTestCase(TestCase):
    def test_email_verification_invalid_token(self):
        """Редирект на главную, если токен неверный или не существует."""
        User.objects.create_user(username='newuser1', email='test@example.com', password='pass123')
        url = reverse(
            'users:email_verification', kwargs={'email': 'test@example.com', 'code': uuid.uuid4()}
        )
        response = self.client.get(url)
        user = User.objects.get(username='newuser1')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('main:index'))
        self.assertFalse(user.is_verified_email)

    def test_email_verification_valid_token(self):
        """Успешная активация почты при корректном токене."""
        user = User.objects.create_user(
            username='newuser2', email='test1@example.com', password='pass123'
        )
        verification = EmailVerification.objects.create(
            user=user, code=uuid.uuid4(), expiration=(timezone.now() + timedelta(hours=1))
        )
        url = reverse(
            'users:email_verification', kwargs={'email': user.email, 'code': verification.code}
        )
        response = self.client.get(url)
        user = User.objects.get(username='newuser2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(user.is_verified_email)
        self.assertTemplateUsed(response, 'users/email_verification.html')

    def test_email_verification_expired_token(self):
        """Редирект на главную, если токен подтверждения почты истёк."""
        user = User.objects.create_user(
            username='newuser3', email='test2@example.com', password='pass123'
        )
        verification = EmailVerification.objects.create(
            user=user, code=uuid.uuid4(), expiration=(timezone.now() - timedelta(hours=1))
        )
        url = reverse(
            'users:email_verification', kwargs={'email': user.email, 'code': verification.code}
        )
        response = self.client.get(url)
        user = User.objects.get(username='newuser3')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('main:index'))
        self.assertFalse(user.is_verified_email)

    def test_email_change_token_valid(self):
        """Смена email при корректном токене подтверждения."""
        token = uuid.uuid4()
        user = User.objects.create_user(
            username='newuser4',
            email='test4@example.com',
            new_email='test5@example.com',
            email_change_token=token,
        )
        url = reverse('users:email_verification', kwargs={'email': user.email, 'code': token})
        response = self.client.get(url)
        user = User.objects.get(username='newuser4')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.email, 'test5@example.com')
        self.assertEqual(user.new_email, None)
        self.assertEqual(user.email_change_token, None)


class ChangeEmailViewTestCase(TestCase):
    @patch('users.views.ChangeEmailView.send_confirmation_email')
    def test_send_confirmation_email_sends_to_correct_address(self, mock_send):
        """Проверяет, что при запросе смены email вызывается метод отправки письма
        и он вызывается ровно один раз с правильным пользователем.
        """
        user = User.objects.create_user(username='newuser', email='test@example.com', password='pass123')
        self.client.force_login(user)
        url = reverse('users:email_reset')
        self.client.post(url, {'new_email': 'new@example.com'})
        mock_send.assert_called_once_with(user, ANY)

    def test_generate_confirmation_url_returns_valid_link(self):
        """Проверяет, что метод generate_confirmation_url создаёт корректную ссылку
        с параметрами confirm_email_change и new_email.
        """

        view = ChangeEmailView()
        user = User.objects.create_user(
            username='newuser1', email='test1@example.com', password='pass123'
        )
        mock_request = Mock()
        mock_request.build_absolute_uri.return_value = (
            'http://testserver/users/confirm_email_change/test2@example.com'
        )
        view.request = mock_request
        url = view.generate_confirmation_url(user, new_email='test2@example.com')
        self.assertTrue(isinstance(url, str))
        self.assertIn('confirm_email_change', url)
        self.assertIn('test2@example.com', url)


class ConfirmEmailChangeViewTestCase(TestCase):
    def test_confirm_email_change_invalid_token(self):
        """
        Проверяет поведение при невалидном токене подтверждения email:
        - email пользователя не изменяется;
        - отображается сообщение об ошибке;
        - выполняется редирект на страницу завершения смены email.
        """
        user = User.objects.create_user(
            username='newuser1', email='test1@example.com', password='pass123'
        )
        url = reverse(
            'users:confirm_email_change',
            kwargs={
                'uidb64': str(urlsafe_base64_encode(force_bytes(user.pk))),
                'token': str(uuid.uuid4()),
                'new_email': 'test2@example.com',
            },
        )

        response = self.client.get(url)
        messages = list(get_messages(response.wsgi_request))
        user = User.objects.get(username='newuser1')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('users:email_reset_complete'))
        self.assertEqual(user.email, 'test1@example.com')
        self.assertTrue(any('Ссылка для подтверждения недействительна' in str(m) for m in messages))

    def test_confirm_email_change_nonexistent_user(self):
        """
        Проверяет поведение при несуществующем пользователе (невалидный uidb64):
        - пользователь не найден;
        - отображается сообщение об ошибке;
        - выполняется редирект на страницу завершения смены email.
        """
        uid = force_str(urlsafe_base64_encode(force_bytes(99999)))
        url = reverse(
            'users:confirm_email_change',
            kwargs={
                'uidb64': uid,
                'token': str(uuid.uuid4()),
                'new_email': 'test2@example.com',
            },
        )
        response = self.client.get(url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('users:email_reset_complete'))
        self.assertTrue(any('Ссылка для подтверждения недействительна' in str(m) for m in messages))

    def test_confirm_email_change_valid_token(self):
        """
        Проверяет успешную смену email при корректном токене:
        - email пользователя обновляется на новый;
        - отображается сообщение об успехе;
        - выполняется редирект на страницу завершения смены email.
        """
        user = User.objects.create_user(
            username='newuser1', email='test1@example.com', password='pass123'
        )
        uid = str(urlsafe_base64_encode(force_bytes(user.pk)))
        token = default_token_generator.make_token(user)
        url = reverse(
            'users:confirm_email_change',
            kwargs={
                'uidb64': uid,
                'token': token,
                'new_email': 'test2@example.com',
            },
        )
        response = self.client.get(url)
        messages = list(get_messages(response.wsgi_request))
        user = User.objects.get(username='newuser1')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('users:email_reset_complete'))
        self.assertEqual(user.email, 'test2@example.com')
        self.assertTrue(any('Ваш email успешно изменен!' in str(m) for m in messages))


class LogoutViewTestCase(TestCase):
    def test_logout_redirects_and_ends_session(self):
        """
        Проверяет корректную работу выхода из системы:
        - пользователь разлогинивается (сессия очищается);
        - выполняется редирект на главную страницу.
        """
        user = User.objects.create_user(
            username='newuser1', email='test1@example.com', password='pass123'
        )
        self.client.force_login(user)
        response = self.client.get(reverse('users:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('main:index'))
        self.assertNotIn('_auth_user_id', self.client.session)
