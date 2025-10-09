from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from users.models import EmailVerification
from users.tasks import send_email_verification, send_reset_email


User = get_user_model()


class SendEmailVerificationTaskTestCase(TestCase):
    @patch('users.models.EmailVerification.send_verification_email')
    def test_task_creates_verification_and_calls_send_email(self, mock_send_email):
        """
        Проверяет, что задача создаёт запись EmailVerification
        и вызывает метод отправки письма подтверждения.
        """
        user = User.objects.create_user(
            username='newuser1', email='test1@example.com', password='pass123'
        )
        send_email_verification(user.id)

        verification = EmailVerification.objects.filter(user=user).first()
        self.assertIsNotNone(verification)
        mock_send_email.assert_called_once()

    @patch('users.models.EmailVerification.send_verification_email')
    def test_task_accepts_email_instead_of_id(self, mock_send_email):
        """
        Проверяет, что задача корректно обрабатывает email
        как идентификатор пользователя и выполняет те же действия:
        создаёт запись EmailVerification и вызывает метод отправки письма.
        """
        user = User.objects.create_user(
            username='newuser1', email='test1@example.com', password='pass123'
        )
        send_email_verification(user.email)

        verification = EmailVerification.objects.filter(user=user).first()
        self.assertIsNotNone(verification)
        mock_send_email.assert_called_once()

    def test_task_raises_value_error_if_user_not_found(self):
        """
        Проверяет, что задача вызывает ValueError,
        если пользователь с указанным id или email не найден.
        """
        with self.assertRaises(ValueError) as exc:
            send_email_verification('test1@example.com')
        self.assertIn('User matching query does not exist', str(exc.exception))


class SendResetEmailTaskTestCase(TestCase):
    @patch('users.tasks.send_mail')
    def test_task_sends_email_with_correct_arguments(self, mock_send_mail):
        """
        Проверяет, что задача send_reset_email вызывает функцию send_mail
        с корректными аргументами (тема, сообщение, отправитель и получатель).
        """
        subject = 'Test subject'
        message = 'Reset password message'
        recipient_list = ['user@example.com']
        send_reset_email(subject, message, recipient_list)
        mock_send_mail.assert_called_once()
