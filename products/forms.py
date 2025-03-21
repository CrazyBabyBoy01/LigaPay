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
        label="Автоматическая доставка",
        required=False,
        widget=forms.CheckboxInput(attrs={"value": "True"}),
    )
    seller_is_online = forms.BooleanField(
        label="Только продавцы онлайн",
        help_text="Пометить, если продавец находится в сети",
        required=False,
        widget=forms.CheckboxInput(attrs={"value": "True"}),
    )


class AccountServiceFilterForm(forms.Form):
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
        widget=forms.Select(attrs={"class": "filter-container__server"}),
    )
    filter_type = forms.ChoiceField(
        choices=[
            ("", "Выберите категорию"),
            ("sell", "Продажа"),
            ("rent", "Аренда"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "filter-container__btn"}),
    )
    rank = forms.ChoiceField(
        choices=[
            ("", "Выберите ранг"),
            ("IRON", "Железо"),
            ("BRONZE", "Бронза"),
            ("SILVER", "Серебро"),
            ("GOLD", "Золото"),
            ("PLATINUM", "Платина"),
            ("EMERALD", "Изумруд"),
            ("DIAMOND", "Алмаз"),
            ("MASTER", "Мастер"),
            ("GRANDMASTER", "Гранмастер"),
            ("CHALLENGER", "Претендент"),
            ("NO_RANK", "Нет ранга"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "filter-container__rank"}),
    )
    is_auto_delivery = forms.BooleanField(
        help_text="Пометить, если услуга поддерживает автоматическую доставку",
        label="Автоматическая доставка",
        required=False,
        widget=forms.CheckboxInput(attrs={"value": "True"}),
    )
    seller_is_online = forms.BooleanField(
        label="Только продавцы онлайн",
        help_text="Пометить, если продавец находится в сети",
        required=False,
        widget=forms.CheckboxInput(attrs={"value": "True"}),
    )
    character_count_min = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(
            attrs={"id": "character_count_min", "name": "character_count_min", "placeholder": "От"}
        ),
    )
    character_count_max = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(
            attrs={"id": "character_counts_max", "name": "character_counts_max", "placeholder": "До"}
        ),
    )
    account_level_min = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={"id": "account_level_min", "name": "account_level_min", "placeholder": "От"}),
    )
    account_level_max = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={"id": "account_level_max", "name": "account_level_max", "placeholder": "До"}),
    )

    skin_count_min = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={"id": "skin_count_min", "name": "skin_count_min", "placeholder": "От"}),
    )
    skin_count_max = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={"id": "skin_count_max", "name": "skin_count_max", "placeholder": "До"}),
    )
    search = forms.CharField(
        required=False, label="Поиск", widget=forms.TextInput(attrs={"placeholder": "Введите название или описание"})
    )


class BoostServiceFilterForm(forms.Form):
    server = forms.ChoiceField(
        choices=[
            ("", "Выберите сервер"),
            ("nordic", "EU Nordic & East"),
            ("west", "EU West"),
            ("japan", "Japan"),
            ("north", "Latin America North"),
            ("south", "Latin America South"),
            ("namerica", "North America"),
            ("russia", "Russia"),
            ("turkey", "Turkey"),
            ("other", "Другой сервер"),
        ],
        required=False,
        widget=forms.Select(attrs={"id": "server", "class": "filter-container__server"}),
    )
    filter_type = forms.ChoiceField(
        choices=[
            ("", "Вид буста"),
            ("solo", "Соло буст"),
            ("duo", "Дуо буст"),
        ],
        required=False,
        widget=forms.Select(attrs={"id": "serversdsd", "class": "filter-container__btn"}),
    )
    rank_range = forms.ChoiceField(
        choices=[
            ("", "Диапазон буста"),
            ("IRON_BRONZE", "Железо 4 - Бронза 4"),
            ("BRONZE_SILVER", "Бронза 4 - Серебро 4"),
            ("SILVER_GOLD", "Серебро 4 - Золото 4"),
            ("GOLD_PLATINUM", "Золото 4 - Платина 4"),
            ("PLATINUM_EMERALD", "Платина 4 - Изумруд 4"),
            ("EMERALD_DIAMOND", "Изумруд 4 - Алмаз 4"),
            ("DIAMOND_MASTER", "Алмаз 4 - Мастер"),
            ("MASTER_GRANDMASTER", "Мастер - Грандмастер"),
            ("GRANDMASTER_PRETENDER", "Грандмастер - Претендент"),
        ],
        required=False,
        widget=forms.Select(attrs={"id": "serversdsd", "class": "filter-container__btn"}),
    )
    seller_is_online = forms.BooleanField(
        label="Только продавцы онлайн",
        help_text="Пометить, если продавец находится в сети",
        required=False,
        widget=forms.CheckboxInput(attrs={"value": "True"}),
    )
    search = forms.CharField(
        required=False, label="Поиск", widget=forms.TextInput(attrs={"placeholder": "Введите название или описание"})
    )


class BoostServiceForm(forms.ModelForm):
    class Meta:
        model = BoostService
        fields = [
            "title",  # Из BaseService
            "description",  # Из BaseService
            "price",  # Из BaseService
            "filter_type",
            "server",
            "is_auto_delivery",
            "rank_range",
        ]


class TrainingServiceFilterForm(forms.Form):
    filter_type = forms.ChoiceField(
        choices=[
            ("top", "Топ"),
            ("jungle", "Лес"),
            ("mid", "Мид"),
            ("adc", "АДК"),
            ("support", "Сап"),
            ("any role", "Любая роль"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "filter-container__btn"}),
    )
    seller_is_online = forms.BooleanField(
        label="Только продавцы онлайн",
        help_text="Пометить, если продавец находится в сети",
        required=False,
        widget=forms.CheckboxInput(attrs={"value": "True"}),
    )
    search = forms.CharField(
        required=False, label="Поиск", widget=forms.TextInput(attrs={"placeholder": "Введите название или описание"})
    )


class TrainingServiceForm(forms.ModelForm):
    class Meta:
        model = TrainingService
        fields = [
            "title",  # Из BaseService
            "description",  # Из BaseService
            "price",  # Из BaseService
            "filter_type",
            "seller_is_online",
        ]


class BattlePassServiceFilterForm(forms.Form):
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
            ("", "Количество RP"),
            ("1650 RP", "1650 RP"),
            ("2650 RP", "2650 RP"),
            ("3650 RP", "3650 RP"),
        ],
        required=False,
        widget=forms.Select(attrs={"id": "serversdsd", "class": "filter-container__btn"}),
    )
    is_auto_delivery = forms.BooleanField(
        help_text="Пометить, если услуга поддерживает автоматическую доставку",
        label="Автоматическая доставка",
        required=False,
        widget=forms.CheckboxInput(attrs={"value": "True"}),
    )
    seller_is_online = forms.BooleanField(
        label="Только продавцы онлайн",
        help_text="Пометить, если продавец находится в сети",
        required=False,
        widget=forms.CheckboxInput(attrs={"value": "True"}),
    )


class BattlePassServiceForm(forms.ModelForm):
    class Meta:
        model = BattlePassService
        fields = [
            "title",  # Из BaseService
            "description",  # Из BaseService
            "price",  # Из BaseService
            "filter_type",
            "seller_is_online",
            "is_auto_delivery",
            "server",
            "quantity",
        ]


class DonationServiceFilterForm(forms.Form):
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
            ("chests", "Сундуки"),
            ("chests_with_keys", "Сундуки+ключи"),
            ("skins", "Скины"),
            ("spheres", "Сферы"),
            ("other", "Прочее"),
        ],
        required=False,
        widget=forms.Select(attrs={"id": "serversdsd", "class": "filter-container__btn"}),
    )
    receiving_method = forms.ChoiceField(
        choices=[
            ("", "Способ получения"),
            ("GIFT", "Подарком"),
            ("LOGIN", "С заходом на аккаунт"),
        ],
        required=False,
        widget=forms.Select(attrs={"id": "serversdsd", "class": "filter-container__btn"}),
    )
    is_auto_delivery = forms.BooleanField(
        help_text="Пометить, если услуга поддерживает автоматическую доставку",
        label="Автоматическая доставка",
        required=False,
        widget=forms.CheckboxInput(attrs={"value": "True"}),
    )
    seller_is_online = forms.BooleanField(
        label="Только продавцы онлайн",
        help_text="Пометить, если продавец находится в сети",
        required=False,
        widget=forms.CheckboxInput(attrs={"value": "True"}),
    )
    search = forms.CharField(
        required=False, label="Поиск", widget=forms.TextInput(attrs={"placeholder": "Введите название или описание"})
    )


class DonationServiceForm(forms.ModelForm):
    class Meta:
        model = DonationService
        fields = [
            "title",  # Из BaseService
            "description",  # Из BaseService
            "price",  # Из BaseService
            "filter_type",
            "seller_is_online",
            "is_auto_delivery",
            "server",
            "receiving_method",
        ]


class GeneralServiceFilterForm(forms.Form):
    filter_type = forms.ChoiceField(
        choices=[
            ("", "Выберите категорию"),
            ("battle_pass_boost", "Прокачка боевого пропуска"),
            ("champion_mastery_boost", "Прокачка мастерства чемпиона"),
            ("aram", "ARAM"),
            ("clash", "Clash"),
            ("normal_game", "Обычная игра"),
            ("cooperative_game", "Совместная игра"),
            ("leaverbuster_recovery", "Отыгрыш ливбустера"),
            ("chat_ban_recovery", "Отыгрыш банчата"),
            ("account_leveling", "Прокачка уровня аккаунта"),
            ("mastery_token_farm", "Фарм жетонов мастерства"),
            ("deboost", "Дебуст"),
        ],
        required=False,
        widget=forms.Select(attrs={"id": "serversdsd", "class": "filter-container__btn"}),
    )
    seller_is_online = forms.BooleanField(
        label="Только продавцы онлайн",
        help_text="Пометить, если продавец находится в сети",
        required=False,
        widget=forms.CheckboxInput(attrs={"value": "True"}),
    )
    search = forms.CharField(
        required=False, label="Поиск", widget=forms.TextInput(attrs={"placeholder": "Введите название или описание"})
    )


class GeneralServiceForm(forms.ModelForm):
    class Meta:
        model = GeneralService
        fields = [
            "title",  # Из BaseService
            "description",  # Из BaseService
            "price",  # Из BaseService
            "filter_type",
            "seller_is_online",
        ]


class QualificationServiceFilterForm(forms.Form):
    server = forms.ChoiceField(
        choices=[
            ("", "Выберите сервер"),
            ("nordic", "EU Nordic & East"),
            ("west", "EU West"),
            ("japan", "Japan"),
            ("north", "Latin America North"),
            ("south", "Latin America South"),
            ("namerica", "North America"),
            ("russia", "Russia"),
            ("turkey", "Turkey"),
        ],
        required=False,
        widget=forms.Select(attrs={"id": "server", "class": "filter-container__server"}),
    )
    seller_is_online = forms.BooleanField(
        label="Только продавцы онлайн",
        help_text="Пометить, если продавец находится в сети",
        required=False,
        widget=forms.CheckboxInput(attrs={"value": "True"}),
    )
    search = forms.CharField(
        required=False, label="Поиск", widget=forms.TextInput(attrs={"placeholder": "Введите название или описание"})
    )


class QualificationServiceForm(forms.ModelForm):
    class Meta:
        model = QualificationService
        fields = [
            "title",  # Из BaseService
            "description",  # Из BaseService
            "price",  # Из BaseService
            "server",
            "seller_is_online",
        ]


class OtherServiceFilterForm(forms.Form):
    filter_type = forms.ChoiceField(
        choices=[
            ("", "Выберите категорию"),
            ("guides", "Гайды"),
            ("other", "Прочее"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "filter-container__btn"}),
    )
    is_auto_delivery = forms.BooleanField(
        help_text="Пометить, если услуга поддерживает автоматическую доставку",
        label="Автоматическая доставка",
        required=False,
        widget=forms.CheckboxInput(attrs={"value": "True"}),
    )
    seller_is_online = forms.BooleanField(
        label="Только продавцы онлайн",
        help_text="Пометить, если продавец находится в сети",
        required=False,
        widget=forms.CheckboxInput(attrs={"value": "True"}),
    )
    search = forms.CharField(
        required=False, label="Поиск", widget=forms.TextInput(attrs={"placeholder": "Введите название или описание"})
    )


class OtherServiceForm(forms.ModelForm):
    class Meta:
        model = OtherService
        fields = [
            "title",  # Из BaseService
            "description",  # Из BaseService
            "price",  # Из BaseService
            "filter_type",
            "is_auto_delivery",
            "quantity",
        ]


class PurchaseForm(forms.Form):
    payment_method = forms.ChoiceField(
        choices=[("", "Не выбран"), ("method1", "Банковская карта RU"), ("method2", "СБП (оплата по QR)")],
        label="Способ оплаты",
        required=True,
        widget=forms.Select(attrs={"class": "details-form__item"}),
    )
    amount = forms.IntegerField(
        label="Получу",
        required=True,
        widget=forms.NumberInput(
            attrs={"class": "details-form__item", "id": "amount", "placeholder": "Введите количество"}
        ),
    )
    price = forms.DecimalField(
        label="Заплачу",
        required=True,
        widget=forms.NumberInput(
            attrs={
                "class": "details-form__item",
                "id": "price",
                "placeholder": "Стоимость в рублях",
                "readonly": "readonly",
            }
        ),
    )
    player_id = forms.CharField(
        label="Идентификатор игрока",
        required=True,
        widget=forms.TextInput(attrs={"class": "details-form__item", "placeholder": "Введите идентификатор игрока"}),
    )
