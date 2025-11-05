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


CATEGORY_MODEL_MAPPING = {
    'accounts': AccountService,
    'training': TrainingService,
    'donation': DonationService,
    'general': GeneralService,
}


class ServiceImageForm(forms.ModelForm):
    """
    Форма для загрузки изображения к услуге.
    Поддерживает необязательное поле image.
    """
    image = forms.ImageField(required=False, label='Загрузить изображение')

    class Meta:
        model = ServiceImage
        fields = ['image']


class AccountServiceForm(forms.ModelForm):
    """
    Форма для создания и редактирования услуг категории «Аккаунты».

    Включает стандартные поля из BaseService и уникальные характеристики аккаунта:
    ранг, сервер, уровень, количество скинов и персонажей.
    """

    class Meta:
        model = AccountService
        fields = [
            'title',
            'description',
            'price',
            'filter_type',
            'rank',
            'server',
            'account_level',
            'skin_count',
            'character_count',
            'is_auto_delivery',
            'quantity',
        ]


class RPServiceForm(forms.ModelForm):
    """
    Форма для услуг категории «RP» (внутриигровая валюта).

    Используется для создания и редактирования предложений по продаже RP.
    """

    class Meta:
        model = RPService
        fields = [
            'title',
            'description',
            'price',
            'filter_type',
            'server',
            'quantity',
            'is_auto_delivery',
        ]


class RPServiceFilterForm(forms.Form):
    """
    Форма фильтрации списка RP-услуг.
    Позволяет фильтровать по серверу, типу сделки, авто-доставке и онлайн-статусу продавца.
    """
    server = forms.ChoiceField(
        choices=SERVER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'id': 'server', 'class': 'filter-container__server'}),
    )
    filter_type = forms.ChoiceField(
        choices=RP_FILTER_CHOICES,
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


class AccountServiceFilterForm(forms.Form):
    """
    Форма фильтрации аккаунтов по параметрам:
    сервер, тип сделки, ранг, уровень, количество скинов/персонажей и авто-доставка.
    """
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
    """
    Форма фильтрации услуг буста.
    Поддерживает фильтрацию по серверу, типу сделки, диапазону рангов и активности продавца.
    """
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
    """
    Форма для создания и редактирования услуг категории «Буст».
    Включает базовые поля и параметры диапазона рангов.
    """
    class Meta:
        model = BoostService
        fields = [
            'title',
            'description',
            'price',
            'filter_type',
            'server',
            'is_auto_delivery',
            'rank_range',
        ]


class TrainingServiceFilterForm(forms.Form):
    """
    Форма фильтрации услуг обучения.
    Позволяет отбирать предложения по типу и онлайн-статусу продавца.
    """
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
    """
    Форма для создания и редактирования услуг категории «Обучение».
    Используется для добавления предложений по тренировкам.
    """
    class Meta:
        model = TrainingService
        fields = [
            'title',
            'description',
            'price',
            'filter_type',
            'seller_is_online',
        ]


class BattlePassServiceFilterForm(forms.Form):
    """
    Форма фильтрации услуг категории «Боевой пропуск».
    Позволяет фильтровать по серверу, типу сделки и авто-доставке.
    """
    server = forms.ChoiceField(
        choices=SERVER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'id': 'server', 'class': 'filter-container__server'}),
    )
    filter_type = forms.ChoiceField(
        choices=BP_FILTER_CHOICES,
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


class BattlePassServiceForm(forms.ModelForm):
    """
    Форма для создания и редактирования услуг категории «Боевой пропуск».
    Содержит поля сервера, авто-доставки и количества.
    """
    class Meta:
        model = BattlePassService
        fields = [
            'title',
            'description',
            'price',
            'filter_type',
            'seller_is_online',
            'is_auto_delivery',
            'server',
            'quantity',
        ]


class DonationServiceFilterForm(forms.Form):
    """
    Форма фильтрации донат-услуг.
    Позволяет отбирать предложения по серверу, типу сделки, авто-доставке и способу получения.
    """
    server = forms.ChoiceField(
        choices=SERVER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'id': 'server', 'class': 'filter-container__server'}),
    )
    filter_type = forms.ChoiceField(
        choices=DONATION_FILTER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'filter-container__btn'}),
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
    """
    Форма для создания и редактирования услуг категории «Донат».
    Включает выбор способа получения (receiving_method) и сервера.
    """
    class Meta:
        model = DonationService
        fields = [
            'title',
            'description',
            'price',
            'filter_type',
            'seller_is_online',
            'is_auto_delivery',
            'server',
            'receiving_method',
        ]


class GeneralServiceFilterForm(forms.Form):
    """
    Форма фильтрации общих услуг.
    Позволяет искать предложения по типу и онлайн-статусу продавца.
    """
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
    """
    Форма для создания и редактирования общих услуг.
    Используется для универсальных предложений без особых параметров.
    """
    class Meta:
        model = GeneralService
        fields = [
            'title',
            'description',
            'price',
            'filter_type',
            'seller_is_online',
        ]


class QualificationServiceFilterForm(forms.Form):
    """
    Форма фильтрации квалификационных услуг.
    Позволяет искать предложения по серверу и онлайн-статусу продавца.
    """
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
    """
    Форма для создания и редактирования услуг категории «Квалификация».
    Содержит поля сервера и информации о продавце.
    """
    class Meta:
        model = QualificationService
        fields = [
            'title',
            'description',
            'server',
            'seller_is_online',
        ]


class OtherServiceFilterForm(forms.Form):
    """
    Форма фильтрации услуг категории «Прочее».
    Позволяет отбирать предложения по типу, авто-доставке и активности продавца.
    """
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
    """
    Форма для создания и редактирования услуг категории «Прочее».
    Используется для дополнительных предложений, не входящих в другие категории.
    """
    class Meta:
        model = OtherService
        fields = [
            'title',
            'description',
            'price',
            'filter_type',
            'is_auto_delivery',
            'quantity',
        ]


class PurchaseForm(forms.Form):
    """
    Форма оформления покупки услуги.

    Позволяет выбрать способ оплаты, указать количество, итоговую цену и идентификатор игрока.
    """
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
