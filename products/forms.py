from attr import fields
from django import forms

from .models import (
    AccountService,
    BattlePassService,
    BoostService,
    DonationService,
    GeneralService,
    OtherService,
    QualificationService,
    RPService,
    ServerBasedService,
    TrainingService,
)


# Сопоставление моделей категориям
CATEGORY_MODEL_MAPPING = {
    "accounts": AccountService,
    "training": TrainingService,
    "donation": DonationService,
    "general": GeneralService,
}


class AccountServiceForm(forms.ModelForm):
    """
    Форма для создания и редактирования услуг категории 'AccountService',
    включая поля, унаследованные от BaseService.
    """

    class Meta:
        model = AccountService
        fields = [
            "title",  # Из BaseService
            "description",  # Из BaseService
            "price",  # Из BaseService
            "filter_type",
            "rank",  # Уникальное для AccountService
            "server",  # Уникальное для AccountService
            "account_level",  # Уникальное для AccountService
            "skin_count",  # Уникальное для AccountService
            "character_count",  # Уникальное для AccountService
            "is_auto_delivery",
        ]


# class RPServiceFilterForm(forms.ModelForm):
#     class Meta:
#         model = RPService
#         fields = ["server", "filter_type"]

#     server = forms.ModelChoiceField(
#         choices=RPService.SERVER_CHOICES,
#         widget=forms.Select(attrs={"class": "filter-container__server"}),
#     )
#     filter_type = forms.ChoiceField(
#         choices=RPService.FILTER_CHOICES, widget=forms.Select(attrs={"class": "filter-container__btn"})
#     )


class RPServiceForm(forms.ModelForm):
    class Meta:
        model = RPService
        fields = [
            "title",  # Из BaseService
            "description",  # Из BaseService
            "price",  # Из BaseService
            "filter_type",
            "server",
            "quantity",
            "is_auto_delivery",
        ]


class RPServiceFilterForm(forms.Form):
    server = forms.ChoiceField(
        choices=[
            ("", "Выберите сервер"),
            ("nordic", "EU Nordic & East"),
            ("west", "EU West"),
            ("japan", "Japan"),
            ("north", "Latin America North"),
            ("south", "Latin America South"),
            ("russia", "Russia"),
            ("turkey", "Turkey"),
        ],
        required=False,
        widget=forms.Select(attrs={"id": "server", "class": "filter-container__server"}),
    )
    filter_type = forms.ChoiceField(
        choices=[
            ("", "Выберите категорию"),
            ("gifts_for_rp", "Подарки за RP"),
            ("prepaid_cards", "Карты предоплаты"),
            ("rp_account", "RP с заходом на аккаунт"),
        ],
        required=False,
        widget=forms.Select(attrs={"id": "serversdsd", "class": "filter-container__btn"}),
    )
    is_auto_delivery = forms.BooleanField(
        help_text="Пометить, если услуга поддерживает автоматическую доставку",
        label="Только продавцы онлайн",
        required=False,
        widget=forms.CheckboxInput(attrs={"value": "True"}),
    )
    seller_is_online = forms.BooleanField(
        label="Автоматическая доставка",
        help_text="Пометить, если продавец находится в сети",
        required=False,
        widget=forms.CheckboxInput(attrs={"value": "True"}),
    )
