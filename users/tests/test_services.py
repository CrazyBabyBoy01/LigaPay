import uuid
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.timezone import now

from users.models import EmailVerification
from users.services import send_verification_email


User = get_user_model()


class SendVerificationEmailServiceTestCase(TestCase):
    @patch('users.services.send_mail')
    def test_send_verification_email_calls_send_mail_with_correct_arguments(self, mock_send_mail):
        """
        Проверяет, что функция отправки письма подтверждения
        вызывает send_mail с корректными параметрами.
        """
        user = User.objects.create_user(
            username='newuser', email='test@example.com', password='pass1234'
        )
        verification = EmailVerification.objects.create(user=user, expiration=now(), code=uuid.uuid4())
        send_verification_email(verification)
        mock_send_mail.assert_called_once()
        args, kwargs = mock_send_mail.call_args
        self.assertIn(user.email, kwargs['recipient_list'])
        self.assertIn(user.username, kwargs['subject'])
        self.assertIn(user.email, kwargs['message'])
        self.assertIn('http', kwargs['message'])
