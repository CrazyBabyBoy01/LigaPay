from django import forms

from .choices import (
    ACCOUNT_FILTER_CHOICES,
    BOOST_FILTER_CHOICES,
    BP_FILTER_CHOICES,
    DONATION_FILTER_CHOICES,
    GENERAL_FILTER_CHOICES,
    OTHER_FILTER_CHOICES,
    RANK_CHOICES,
    RANK_RANGE_CHOICES,
    RECEIVING_METHOD_CHOICES,
    RP_FILTER_CHOICES,
    SERVER_CHOICES,
    TRAINING_FILTER_CHOICES,
)
from .models import (
    AccountService,
    BattlePassService,
    BoostService,
    DonationService,
    GeneralService,
    OtherService,
    QualificationService,
    RPService,
    ServiceImage,
    TrainingService,
)


# Сопоставление моделей категориям
CATEGORY_MODEL_MAPPING = {
    'accounts': AccountService,
    'training': TrainingService,
    'donation': DonationService,
    'general': GeneralService,
}


class ServiceImageForm(forms.ModelForm):
    image = forms.ImageField(required=False, label='Загрузить изображение')

    class Meta:
        model = ServiceImage
        fields = ['image']


class AccountServiceForm(forms.ModelForm):
    """
    Форма для создания и редактирования услуг категории 'AccountService',
    включая поля, унаследованные от BaseService.
    """

    class Meta:
        model = AccountService
        fields = [
            'title',  # Из BaseService
            'description',  # Из BaseService
            'price',  # Из BaseService
            'filter_type',
            'rank',  # Уникальное для AccountService
            'server',  # Уникальное для AccountService
            'account_level',  # Уникальное для AccountService
            'skin_count',  # Уникальное для AccountService
            'character_count',  # Уникальное для AccountService
            'is_auto_delivery',
            'quantity',
        ]


class RPServiceForm(forms.ModelForm):
    class Meta:
        model = RPService
        fields = [
            'title',  # Из BaseService
            'description',  # Из BaseService
            'price',  # Из BaseService
            'filter_type',
            'server',
            'quantity',
            'is_auto_delivery',
        ]


class RPServiceFilterForm(forms.Form):
    server = forms.ChoiceField(
        choices=SERVER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'id': 'server', 'class': 'filter-container__server'}),
    )
    filter_type = forms.ChoiceField(
        choices=RP_FILTER_CHOICES,
        required=False,
        widget=forms.Select(attrs={ 'class': 'filter-container__btn'}),
    )
    is_auto_delivery = forms.BooleanField(
        help_text='Пометить, если услуга поддерживает автоматическую доставку',
        label='Автоматическая доставка',
        required=False,
        widget=forms.CheckboxInput(),
    )
    seller_is_online = forms.BooleanField(
        label='Только продавцы онлайн',
        help_text='Пометить, если продавец находится в сети',
        required=False,
        widget=forms.CheckboxInput(),
    )


class AccountServiceFilterForm(forms.Form):
    server = forms.ChoiceField(
        choices=SERVER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'filter-container__server'}),
    )
    filter_type = forms.ChoiceField(
        choices=ACCOUNT_FILTER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'filter-container__btn'}),
    )
    rank = forms.ChoiceField(
        choices=RANK_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'filter-container__rank'}),
    )
    is_auto_delivery = forms.BooleanField(
        help_text='Пометить, если услуга поддерживает автоматическую доставку',
        label='Автоматическая доставка',
        required=False,
        widget=forms.CheckboxInput(),
    )
    seller_is_online = forms.BooleanField(
        label='Только продавцы онлайн',
        help_text='Пометить, если продавец находится в сети',
        required=False,
        widget=forms.CheckboxInput(),
    )
    character_count_min = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'id': 'character_count_min', 'placeholder': 'От'}),
    )
    character_count_max = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'id': 'character_count_max', 'placeholder': 'До'}),
    )
    account_level_min = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'id': 'account_level_min', 'placeholder': 'От'}),
    )
    account_level_max = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'id': 'account_level_max', 'placeholder': 'До'}),
    )

    skin_count_min = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'id': 'skin_count_min', 'placeholder': 'От'}),
    )
    skin_count_max = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'id': 'skin_count_max', 'placeholder': 'До'}),
    )
    q = forms.CharField(
        required=False,
        label='Поиск',
        widget=forms.TextInput(attrs={'placeholder': 'Введите название или описание'}),
    )


class BoostServiceFilterForm(forms.Form):
    server = forms.ChoiceField(
        choices=SERVER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'id': 'server', 'class': 'filter-container__server'}),
    )
    filter_type = forms.ChoiceField(
        choices=BOOST_FILTER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'filter-container__btn'}),
    )
    rank_range = forms.ChoiceField(
        choices=RANK_RANGE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'filter-container__btn'}),
    )
    seller_is_online = forms.BooleanField(
        label='Только продавцы онлайн',
        help_text='Пометить, если продавец находится в сети',
        required=False,
        widget=forms.CheckboxInput(),
    )
    q = forms.CharField(
        required=False,
        label='Поиск',
        widget=forms.TextInput(attrs={'placeholder': 'Введите название или описание'}),
    )


class BoostServiceForm(forms.ModelForm):
    class Meta:
        model = BoostService
        fields = [
            'title',  # Из BaseService
            'description',  # Из BaseService
            'price',  # Из BaseService
            'filter_type',
            'server',
            'is_auto_delivery',
            'rank_range',
        ]


class TrainingServiceFilterForm(forms.Form):
    filter_type = forms.ChoiceField(
        choices=TRAINING_FILTER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'filter-container__btn'}),
    )
    seller_is_online = forms.BooleanField(
        label='Только продавцы онлайн',
        help_text='Пометить, если продавец находится в сети',
        required=False,
        widget=forms.CheckboxInput(),
    )
    q = forms.CharField(
        required=False,
        label='Поиск',
        widget=forms.TextInput(attrs={'placeholder': 'Введите название или описание'}),
    )


class TrainingServiceForm(forms.ModelForm):
    class Meta:
        model = TrainingService
        fields = [
            'title',  # Из BaseService
            'description',  # Из BaseService
            'price',  # Из BaseService
            'filter_type',
            'seller_is_online',
        ]


class BattlePassServiceFilterForm(forms.Form):
    server = forms.ChoiceField(
        choices=SERVER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'id': 'server', 'class': 'filter-container__server'}),
    )
    filter_type = forms.ChoiceField(
        choices=BP_FILTER_CHOICES,
        required=False,
        widget=forms.Select(attrs={ 'class': 'filter-container__btn'}),
    )
    is_auto_delivery = forms.BooleanField(
        help_text='Пометить, если услуга поддерживает автоматическую доставку',
        label='Автоматическая доставка',
        required=False,
        widget=forms.CheckboxInput(),
    )
    seller_is_online = forms.BooleanField(
        label='Только продавцы онлайн',
        help_text='Пометить, если продавец находится в сети',
        required=False,
        widget=forms.CheckboxInput(),
    )


class BattlePassServiceForm(forms.ModelForm):
    class Meta:
        model = BattlePassService
        fields = [
            'title',  # Из BaseService
            'description',  # Из BaseService
            'price',  # Из BaseService
            'filter_type',
            'seller_is_online',
            'is_auto_delivery',
            'server',
            'quantity',
        ]


class DonationServiceFilterForm(forms.Form):
    server = forms.ChoiceField(
        choices=SERVER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'id': 'server', 'class': 'filter-container__server'}),
    )
    filter_type = forms.ChoiceField(
        choices=DONATION_FILTER_CHOICES,
        required=False,
        widget=forms.Select(attrs={ 'class': 'filter-container__btn'}),
    )
    receiving_method = forms.ChoiceField(
        choices=RECEIVING_METHOD_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'filter-container__btn'}),
    )
    is_auto_delivery = forms.BooleanField(
        help_text='Пометить, если услуга поддерживает автоматическую доставку',
        label='Автоматическая доставка',
        required=False,
        widget=forms.CheckboxInput(),
    )
    seller_is_online = forms.BooleanField(
        label='Только продавцы онлайн',
        help_text='Пометить, если продавец находится в сети',
        required=False,
        widget=forms.CheckboxInput(),
    )
    q = forms.CharField(
        required=False,
        label='Поиск',
        widget=forms.TextInput(attrs={'placeholder': 'Введите название или описание'}),
    )


class DonationServiceForm(forms.ModelForm):
    class Meta:
        model = DonationService
        fields = [
            'title',  # Из BaseService
            'description',  # Из BaseService
            'price',  # Из BaseService
            'filter_type',
            'seller_is_online',
            'is_auto_delivery',
            'server',
            'receiving_method',
        ]


class GeneralServiceFilterForm(forms.Form):
    filter_type = forms.ChoiceField(
        choices=GENERAL_FILTER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'filter-container__btn'}),
    )
    seller_is_online = forms.BooleanField(
        label='Только продавцы онлайн',
        help_text='Пометить, если продавец находится в сети',
        required=False,
        widget=forms.CheckboxInput(),
    )
    q = forms.CharField(
        required=False,
        label='Поиск',
        widget=forms.TextInput(attrs={'placeholder': 'Введите название или описание'}),
    )


class GeneralServiceForm(forms.ModelForm):
    class Meta:
        model = GeneralService
        fields = [
            'title',  # Из BaseService
            'description',  # Из BaseService
            'price',  # Из BaseService
            'filter_type',
            'seller_is_online',
        ]


class QualificationServiceFilterForm(forms.Form):
    server = forms.ChoiceField(
        choices=SERVER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'id': 'server', 'class': 'filter-container__server'}),
    )
    seller_is_online = forms.BooleanField(
        label='Только продавцы онлайн',
        help_text='Пометить, если продавец находится в сети',
        required=False,
        widget=forms.CheckboxInput(),
    )
    q = forms.CharField(
        required=False,
        label='Поиск',
        widget=forms.TextInput(attrs={'placeholder': 'Введите название или описание'}),
    )


class QualificationServiceForm(forms.ModelForm):
    class Meta:
        model = QualificationService
        fields = [
            'title',  # Из BaseService
            'description',  # Из BaseService
            'price',  # Из BaseService
            'server',
            'seller_is_online',
        ]


class OtherServiceFilterForm(forms.Form):
    filter_type = forms.ChoiceField(
        choices=OTHER_FILTER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'filter-container__btn'}),
    )
    is_auto_delivery = forms.BooleanField(
        help_text='Пометить, если услуга поддерживает автоматическую доставку',
        label='Автоматическая доставка',
        required=False,
        widget=forms.CheckboxInput(),
    )
    seller_is_online = forms.BooleanField(
        label='Только продавцы онлайн',
        help_text='Пометить, если продавец находится в сети',
        required=False,
        widget=forms.CheckboxInput(),
    )
    q = forms.CharField(
        required=False,
        label='Поиск',
        widget=forms.TextInput(attrs={'placeholder': 'Введите название или описание'}),
    )


class OtherServiceForm(forms.ModelForm):
    class Meta:
        model = OtherService
        fields = [
            'title',  # Из BaseService
            'description',  # Из BaseService
            'price',  # Из BaseService
            'filter_type',
            'is_auto_delivery',
            'quantity',
        ]


class PurchaseForm(forms.Form):
    payment_method = forms.ChoiceField(
        choices=[
            ('', 'Не выбран'),
            ('method1', 'Банковская карта RU'),
            ('method2', 'СБП (оплата по QR)'),
        ],
        label='Способ оплаты',
        required=True,
        widget=forms.Select(attrs={'class': 'details-form__item'}),
    )
    amount = forms.IntegerField(
        label='Получу',
        required=False,
        initial=1,
        widget=forms.NumberInput(
            attrs={'class': 'details-form__item', 'id': 'amount', 'placeholder': 'Введите количество'}
        ),
    )
    price = forms.DecimalField(
        label='Заплачу',
        required=False,
        widget=forms.NumberInput(
            attrs={
                'class': 'details-form__item',
                'id': 'price',
                'placeholder': 'Стоимость в рублях',
                'readonly': 'readonly',
            }
        ),
    )
    player_id = forms.CharField(
        label='Идентификатор игрока',
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'details-form__item', 'placeholder': 'Введите идентификатор игрока'}
        ),
    )
