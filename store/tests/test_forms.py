from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, mock_open, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from store.forms import SkinsOrderForm
from store.models import SkinsOrder
from wallet.models import Wallet


User = get_user_model()


class TestSkinsOrderForm(TestCase):
    """
    Тесты для SkinsOrderForm.
    Проверяем только бизнес-логику:
    - наличие кошелька
    - проверку баланса
    - работу save() с кошельком.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='12345',
        )

    @patch('store.forms.Wallet.objects.get')
    def test_clean_raises_error_if_wallet_does_not_exist(self, mock_wallet_get):
        """
        Если у пользователя нет кошелька, clean() должен добавить
        ValidationError 'У вас нет кошелька...'.
        """
        mock_wallet_get.side_effect = Wallet.DoesNotExist()

        form = SkinsOrderForm(
            data={
                'char_name': '',
                'skin_name': '',
                'price_char': '',
                'price_skin': '',
                'server': 'west',
                'account_name': 'SomeName',
            }
        )
        form.request = SimpleNamespace(user=self.user)

        self.assertFalse(form.is_valid())
        errors = form.non_field_errors()
        self.assertTrue(errors)
        self.assertIn('У вас нет кошелька', errors[0])

    @patch('store.forms.Wallet.objects.get')
    @patch('store.forms.json.load')
    @patch('store.forms.open', new_callable=mock_open)
    def test_clean_sets_price_char_when_enough_balance(
        self,
        mock_open_file,
        mock_json_load,
        mock_wallet_get,
    ):
        """
        Если указан char_name и в кошельке достаточно средств,
        clean() должен подставить цену персонажа в cleaned_data['price_char']
        и форма должна быть валидна.
        """
        wallet_mock = MagicMock()
        wallet_mock.balance = Decimal('500')
        mock_wallet_get.return_value = wallet_mock

        mock_json_load.return_value = {
            'Ahri': '100',
        }

        form = SkinsOrderForm(
            data={
                'char_name': 'Ahri',
                'skin_name': '',
                'price_char': '',
                'price_skin': '',
                'server': 'west',
                'account_name': 'SomeName',
            }
        )
        form.request = SimpleNamespace(user=self.user)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['price_char'], Decimal('100'))

    @patch('store.forms.Wallet.objects.get')
    def test_save_uses_cleaned_prices_and_calls_wallet_withdraw(self, mock_wallet_get):
        """
        save() должен:
        - проставить user в instance
        - проставить price_skin/price_char из cleaned_data
        - вызвать wallet.withdraw() с нужной суммой.
        """
        wallet_mock = MagicMock()
        mock_wallet_get.return_value = wallet_mock

        form = SkinsOrderForm()
        form.request = SimpleNamespace(user=self.user)
        form.cleaned_data = {
            'price_skin': Decimal('250'),
            'price_char': None,
        }

        form.instance = SkinsOrder(
            account_name='SomeName',
            server='west',
        )

        instance = form.save(commit=False)

        self.assertEqual(instance.user, self.user)
        self.assertEqual(instance.price_skin, Decimal('250'))
        self.assertIsNone(instance.price_char)

        wallet_mock.withdraw.assert_called_once_with(Decimal('250'))
