from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from users.forms import CustomPasswordResetForm, EmailChangeForm, UserRegistrationForm


User = get_user_model()


class UserRegistrationFormTestCase(TestCase):
    @patch('captcha.fields.CaptchaField.clean', return_value='PASSED')
    @patch('users.forms.send_email_verification.delay')
    def test_user_registration_form_creates_user_and_sends_verification(self, mock_delay, mock_captcha):
        """
        Проверяет, что форма регистрации:
        - создаёт нового пользователя при корректных данных;
        - вызывает задачу на отправку письма подтверждения email.
        """
        data = {
            'username': 'newuser',
            'email': 'test@example.com',
            'password1': 'pass12346767',
            'password2': 'pass12346767',
            'captcha_0': 'dummy',
            'captcha_1': 'PASSED',
        }
        form = UserRegistrationForm(data=data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertTrue(User.objects.filter(username='newuser', email='test@example.com').exists())
        mock_delay.assert_called_once_with(user.id)


class СustomPasswordResetFormTestCase(TestCase):
    def test_password_reset_form_finds_user_by_username(self):
        """
        Проверяет, что форма сброса пароля корректно ищет пользователя по имени:
        - форма валидна при передаче username;
        - в cleaned_data['email'] возвращается email пользователя.
        """
        user = User.objects.create_user(
            username='newuser1', email='test1@example.com', password='pass123'
        )
        data = {
            'email': 'newuser1',
        }
        form = CustomPasswordResetForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['email'], user.email)

    def test_password_reset_form_finds_user_by_email(self):
        """
        Проверяет, что форма сброса пароля корректно ищет пользователя по email:
        - форма валидна при передаче email;
        - в cleaned_data['email'] возвращается тот же email пользователя.
        """
        user = User.objects.create_user(
            username='newuser1', email='test1@example.com', password='pass123'
        )
        data = {
            'email': 'test1@example.com',
        }
        form = CustomPasswordResetForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['email'], user.email)

    def test_password_reset_form_invalid_if_user_not_found(self):
        """
        Проверяет поведение формы сброса пароля при отсутствии пользователя:
        - форма не проходит валидацию;
        - отображается сообщение об ошибке о ненайденном пользователе.
        """
        data = {'email': 'nonexistent@example.com'}
        form = CustomPasswordResetForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('Пользователь с таким логином или email не найден.', form.errors['email'])


class EmailChangeFormTestCase(TestCase):
    def test_email_change_form_invalid_if_email_already_exists(self):
        """
        Проверяет, что форма смены email не проходит валидацию,
        если указанный адрес уже используется другим пользователем.
        """
        User.objects.create_user(username='newuser1', email='test1@example.com', password='pass123')
        data = {'new_email': 'test1@example.com'}
        form = EmailChangeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('Этот адрес электронной почты уже занят.', form.errors['new_email'])

    def test_email_change_form_valid_with_unique_email(self):
        """
        Проверяет, что форма смены email проходит валидацию,
        если указан новый уникальный адрес электронной почты.
        """
        User.objects.create_user(username='newuser1', email='test1@example.com', password='pass123')
        data = {'new_email': 'test2@example.com'}
        form = EmailChangeForm(data=data)
        self.assertTrue(form.is_valid())
