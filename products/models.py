from cProfile import label

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from orders.models import Order


# Create your models here.


class Category(models.Model):
    """
    Модель для категорий услуг.
    Например, "Игры", "Услуги", "Аккаунты".
    """

    name = models.CharField(max_length=255, unique=True, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание категории")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL категории")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class BaseService(models.Model):
    """
    Базовая модель для услуг.
    """

    title = models.CharField(max_length=255, verbose_name="Краткое описание")
    description = models.TextField(verbose_name="Подробное описание", blank=True)
    message = models.TextField(verbose_name="Сообщение покупателю после оплаты", blank=True)
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="%(class)s_services", verbose_name="Продавец"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")
    is_active = models.BooleanField(
        default=True, verbose_name="Активное", help_text="Пометить, если предложение активно"
    )
    orders = GenericRelation(Order)  # Добавляем связь с заказами через GenericForeignKey
    search_description = models.TextField(
        verbose_name="Описание для поиска", blank=True, help_text="Введите текст, который будет использован для поиска"
    )
    is_auto_delivery = models.BooleanField(
        default=False,
        verbose_name="Автоматическая доставка",
        help_text="Пометить, если услуга поддерживает автоматическую доставку",
    )
    seller_is_online = models.BooleanField(
        default=False, verbose_name="Продавец онлайн", help_text="Пометить, если продавец находится в сети"
    )

    class Meta:
        abstract = True  # Это базовая модель, она не создаст таблицу в БД.
        ordering = ["-created_at"]  # Сортировка по умолчанию: последние записи первыми.
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self):
        return self.title


class AutoDeliveryFilter(models.Model):
    """
    Базовая модель для услуг, связанных с автовыдачей.
    """

    auto_delivery = models.BooleanField(default=False, verbose_name="Автоматическая выдача")

    class Meta:
        abstract = True  # Эта модель не будет создавать таблицу в базе данных, она только для наследования


class ServerBasedService(BaseService):
    """
    Базовая модель для услуг, связанных с сервером.
    """

    SERVER_CHOICES = [
        ("nordic", "EU Nordic & East"),
        ("west", "EU West"),
        ("japan", "Japan"),
        ("north", "Latin America North"),
        ("south", "Latin America South"),
        ("namerica", "North America"),
        ("russia", "Russia"),
        ("turkey", "Turkey"),
        ("other", "Другой сервер"),
    ]

    server = models.CharField(
        max_length=50,
        choices=SERVER_CHOICES,
        verbose_name="Сервер",
        default="other",
        help_text="Выберите сервер",
    )

    class Meta:
        abstract = True


class RPService(ServerBasedService, AutoDeliveryFilter):
    """
    Модель услуги для продажи RP (внутриигровой валюты).
    Наследуется от базовой модели BaseService.
    """

    FILTER_CHOICES = [
        ("gifts_for_rp", "Подарки за RP"),
        ("prepaid_cards", "Карты предоплаты"),
        ("rp_account", "RP с заходом на аккаунт"),
    ]
    filter_type = models.CharField(
        max_length=50,
        choices=FILTER_CHOICES,
        verbose_name="Тип",
        default="gifts_for_rp",
        help_text="Выберите, к какому фильтру относится эта запись",
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество", help_text="Количество валюты в наличии")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="rp_services", default=1)

    class Meta:
        verbose_name = "Продажа RP"
        verbose_name_plural = "Продажа RP"

    def __str__(self):
        return f"{self.title} - {self.server} - {self.quantity} доступно"


class AccountService(ServerBasedService, AutoDeliveryFilter):
    """
    Модель услуги для продажи игровых аккаунтов.
    Наследуется от базовой модели BaseService.
    """

    FILTER_CHOICES = [
        ("sell", "Продажа"),
        ("rent", "Аренда"),
    ]
    RANK_CHOICES = [
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
    ]

    rank = models.CharField(
        max_length=20,
        choices=RANK_CHOICES,
        default="NO_RANK",  # Значение по умолчанию
        verbose_name="Ранг аккаунта",
    )
    filter_type = models.CharField(
        max_length=50,
        choices=FILTER_CHOICES,
        verbose_name="Тип фильтра",
        help_text="Выберите, к какому фильтру относится эта запись",
        default="sell",
    )
    skin_count = models.PositiveIntegerField(verbose_name="Количество скинов", default=0)
    account_level = models.PositiveIntegerField(verbose_name="Уровень аккаунта", default=1)
    character_count = models.PositiveIntegerField(verbose_name="Количество персонажей", default=1)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="account_services", default=2)
    quantity = models.PositiveIntegerField(
        verbose_name="Количество", help_text="Количество аккаунтов в наличии", default=1
    )

    class Meta:
        verbose_name = "Продажа аккаунтов"
        verbose_name_plural = "Продажа аккаунтов"

    def __str__(self):
        return f"{self.title} - {self.server}"


class DonationService(ServerBasedService):
    """
    Модель услуги для доната.
    Наследуется от базовой модели BaseService.
    """

    FILTER_CHOICES = [
        ("chests", "Сундуки"),
        ("chests_with_keys", "Сундуки+ключи"),
        ("skins", "Скины"),
        ("spheres", "Сферы"),
        ("other", "Прочее"),
    ]
    RECEIVING_METHOD_CHOICES = [
        ("GIFT", "Подарком"),
        ("LOGIN", "С заходом на аккаунт"),
    ]

    receiving_method = models.CharField(
        max_length=10,
        choices=RECEIVING_METHOD_CHOICES,
        default="GIFT",  # Значение по умолчанию
        verbose_name="Способ получения",
    )
    filter_type = models.CharField(
        max_length=50,
        choices=FILTER_CHOICES,
        verbose_name="Тип фильтра",
        help_text="Выберите, к какому фильтру относится эта запись",
        default="chests",
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="donation_services", default=6)

    class Meta:
        verbose_name = "Услуга доната"
        verbose_name_plural = "Услуги доната"

    def __str__(self):
        return f"{self.title} - {self.server}"


class BoostService(ServerBasedService):
    """
    Модель услуги для буста.
    Наследуется от ServerBasedService.
    """

    FILTER_CHOICES = [
        ("solo", "Соло буст"),
        ("duo", "Дуо буст"),
    ]
    RANK_RANGE_CHOICES = [
        ("IRON_BRONZE", "Железо 4 - Бронза 4"),
        ("BRONZE_SILVER", "Бронза 4 - Серебро 4"),
        ("SILVER_GOLD", "Серебро 4 - Золото 4"),
        ("GOLD_PLATINUM", "Золото 4 - Платина 4"),
        ("PLATINUM_EMERALD", "Платина 4 - Изумруд 4"),
        ("EMERALD_DIAMOND", "Изумруд 4 - Алмаз 4"),
        ("DIAMOND_MASTER", "Алмаз 4 - Мастер"),
        ("MASTER_GRANDMASTER", "Мастер - Грандмастер"),
        ("GRANDMASTER_PRETENDER", "Грандмастер - Претендент"),
    ]

    rank_range = models.CharField(
        max_length=21, choices=RANK_RANGE_CHOICES, default="IRON_BRONZE", verbose_name="Диапазон"
    )
    filter_type = models.CharField(
        max_length=50,
        choices=FILTER_CHOICES,
        verbose_name="Тип фильтра",
        help_text="Выберите, к какому фильтру относится эта запись",
        default="default_value",
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="boost_services", default=3)

    class Meta:
        verbose_name = "Услуга буста"
        verbose_name_plural = "Услуги буста"

    def __str__(self):
        return f"{self.title} - {self.server}"


class GeneralService(BaseService):
    """
    Модель универсальной услуги.
    Наследуется от BaseService.
    """

    FILTER_CHOICES = [
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
    ]
    filter_type = models.CharField(
        max_length=50,
        choices=FILTER_CHOICES,
        verbose_name="Тип фильтра",
        help_text="Выберите, к какому фильтру относится эта запись",
        default="default_value",
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="general_services", default=7)

    class Meta:
        verbose_name = "Общая услуга"
        verbose_name_plural = "Общие услуги"

    def __str__(self):
        return self.title


class QualificationService(ServerBasedService, BaseService):
    """
    Модель услуги квалификации.
    Наследуется от ServerBasedService.
    """

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="qualification_services", default=9)

    class Meta:
        verbose_name = "Услуга квалификации"
        verbose_name_plural = "Услуги квалификации"

    def __str__(self):
        return f"{self.title} - {self.server}"


class TrainingService(BaseService):
    """
    Модель услуги обучения.
    Наследуется от BaseService.
    """

    FILTER_CHOICES = [
        ("top", "Топ"),
        ("jungle", "Лес"),
        ("mid", "Мид"),
        ("adc", "АДК"),
        ("support", "Сап"),
        ("any role", "Любая роль"),
    ]
    filter_type = models.CharField(
        max_length=50,
        choices=FILTER_CHOICES,
        verbose_name="Позиция",
        help_text="Выберите, к какому фильтру относится эта запись",
        default="default_value",
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="training_services", default=4)

    class Meta:
        verbose_name = "Услуга обучения"
        verbose_name_plural = "Услуги обучения"

    def __str__(self):
        return self.title


class BattlePassService(ServerBasedService):
    """
    Модель услуги по продаже боевого пропуска.
    Наследуется от BaseService.
    """

    FILTER_CHOICES = [
        ("1650 RP", "1650 RP"),
        ("2650 RP", "2650 RP"),
        ("3650 RP", "3650 RP"),
    ]
    filter_type = models.CharField(
        max_length=50,
        choices=FILTER_CHOICES,
        verbose_name="Тип фильтра",
        help_text="Выберите, к какому фильтру относится эта запись",
        default="default_value",
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество", help_text="Количество валюты в наличии")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="battlepass_services", default=5)

    class Meta:
        verbose_name = "Продажа боевого пропуска"
        verbose_name_plural = "Продажа боевых пропусков"

    def __str__(self):
        return self.title


class OtherService(BaseService, AutoDeliveryFilter):
    """
    Модель услуги для прочих товаров или услуг.
    Наследуется от BaseService.
    """

    FILTER_CHOICES = [
        ("guides", "Гайды"),
        ("other", "Прочее"),
    ]
    filter_type = models.CharField(
        max_length=50,
        choices=FILTER_CHOICES,
        verbose_name="Тип фильтра",
        help_text="Выберите, к какому фильтру относится эта запись",
        default="default_value",
    )
    quantity = models.PositiveIntegerField(
        default=1, verbose_name="Количество", help_text="Количество товара/услуги в наличии"
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="other_services", default=8)

    class Meta:
        verbose_name = "Прочее"
        verbose_name_plural = "Прочее"

    def __str__(self):
        return self.title
