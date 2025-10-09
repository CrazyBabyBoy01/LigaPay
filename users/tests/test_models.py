import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.timezone import now

from LigaPay import settings
from users.models import EmailVerification


User = get_user_model()
code = uuid.uuid4()


class UserModelTest(TestCase):
    def create_user(self, username='testuser'):
        """Создание пользователя"""
        return User.objects.create_user(username=username, email='test@example.com', password='pass1234')

    def test_is_online_true(self):
        """Пользователь онлайн, если активность была недавно"""
        user = self.create_user(username='testuser1')
        user.last_activity = now()
        user.save()
        self.assertTrue(user.is_online())

    def test_is_online_none(self):
        """Пользователь оффлайн, если активности нет"""
        user = self.create_user(username='testuser2')
        user.last_activity = None
        user.save()
        self.assertFalse(user.is_online())

    def test_is_online_false(self):
        """Пользователь оффлайн, если активность была давно"""
        user = self.create_user(username='testuser3')
        user.last_activity = now() - timedelta(minutes=settings.USER_ONLINE_MINUTES + 1)
        user.save()
        self.assertFalse(user.is_online())

    def test_create_user(self):
        """Проверка корректного создания пользователя"""
        user = self.create_user(username='testuser4')
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.email, 'test@example.com')
        self.assertFalse(user.is_verified_email)
        self.assertIsNone(user.new_email)
        self.assertTrue(user.check_password('pass1234'))


class EmailVerificationModelTest(TestCase):
    def create_user(self, email='test@example.com'):
        """Создание пользователя"""
        return User.objects.create_user(username=email.split('@')[0], email=email, password='pass1234')

    def test_is_expired_true(self):
        """Метод is_expired возвращает True, если токен просрочен"""
        user = self.create_user(email='test1@example.com')
        verification = now() - timedelta(hours=1)
        email = EmailVerification.objects.create(user=user, expiration=verification, code=code)
        self.assertTrue(email.is_expired())

    def test_is_expired_false(self):
        """Метод is_expired возвращает False, если токен не просрочен"""
        user = self.create_user(email='test2@example.com')
        verification = now() + timedelta(hours=1)
        email = EmailVerification.objects.create(user=user, expiration=verification, code=code)
        self.assertFalse(email.is_expired())

    def test_str(self):
        """Метод __str__ возвращает корректное строковое представление объекта"""
        user = self.create_user(email='test3@example.com')
        exp = now() + timedelta(hours=1)
        verification = EmailVerification.objects.create(user=user, expiration=exp, code=uuid.uuid4())
        expected = f'EmailVerification object {user.email}'
        self.assertEqual(str(verification), expected)
