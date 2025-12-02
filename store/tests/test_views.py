from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from django.urls import reverse

from store.views import StoreSkinsView


User = get_user_model()


class TestStoreSkinsView(TestCase):
    """
    Тесты логики POST в StoreSkinsView.
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.view = StoreSkinsView.as_view()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='12345'
        )

    @patch('store.views.logger')
    @patch('store.views.redirect')
    def test_post_unauthenticated_user_redirects(self, mock_redirect, mock_logger):
        """
        Если пользователь не авторизован:
        - должен быть redirect('users:authorization')
        - должен быть вызван logger.warning
        - форма не валидируется
        - send_reset_email.delay НЕ вызывается
        """
        request = self.factory.post('/store/skins/', data={})
        request.user = AnonymousUser()

        self.view(request)

        mock_redirect.assert_called_once_with('users:authorization')
        mock_logger.warning.assert_called_once()

    @patch('store.views.messages')
    @patch('store.views.send_reset_email')
    @patch('store.views.render_to_string')
    @patch('store.views.SkinsOrderForm')
    @patch('store.views.logger')
    def test_post_valid_form_creates_order_and_sends_email(
        self,
        mock_logger,
        mock_form_class,
        mock_render_to_string,
        mock_send_email,
        mock_messages,
    ):
        """
        Если форма валидна:
        - form.save() должен быть вызван
        - send_reset_email.delay() должен быть вызван
        - должен быть redirect на main:index
        """
        request = self.factory.post(
            '/store/skins/',
            data={
                'char_name': 'Ahri',
                'skin_name': '',
                'price_char': 100,
                'price_skin': '',
                'server': 'west',
                'account_name': 'Tester',
            },
        )
        request.user = self.user

        # мок формы
        mock_form = MagicMock()
        mock_form.is_valid.return_value = True
        mock_form.cleaned_data = {
            'char_name': 'Ahri',
            'skin_name': '',
        }
        mock_form_class.return_value = mock_form

        response = self.view(request)

        # form.save()
        mock_form.save.assert_called_once()

        # send_reset_email.delay(...)
        mock_send_email.delay.assert_called_once()

        # redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('main:index'))

        # логирование
        mock_logger.info.assert_called()

        # messages.success был вызван
        mock_messages.success.assert_called_once()

    @patch('store.views.SkinsOrderForm')
    @patch('store.views.messages')
    @patch('store.views.render')
    def test_post_invalid_form_renders_with_errors(self, mock_render, mock_messages, mock_form_class):
        """
        Если форма невалидна:
        - вызывается render
        - messages.error вызывается
        - form.save НЕ вызывается
        - send_reset_email.delay НЕ вызывается
        """
        request = self.factory.post('/store/skins/', data={})
        request.user = self.user

        # Мокаем форму
        mock_form = MagicMock()
        mock_form.is_valid.return_value = False
        mock_form_class.return_value = mock_form

        self.view(request)

        mock_render.assert_called_once()
        mock_messages.error.assert_called_once()
        mock_form.save.assert_not_called()
