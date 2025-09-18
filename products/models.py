from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from orders.models import Order

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


# Create your models here.


class Category(models.Model):
    """
    Модель для категорий услуг.
    Например, "Игры", "Услуги", "Аккаунты".
    """

    name = models.CharField(max_length=255, unique=True, verbose_name='Название категории')
    description = models.TextField(blank=True, verbose_name='Описание категории')
    slug = models.SlugField(max_length=255, unique=True, verbose_name='URL категории')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class BaseService(models.Model):
    """
    Базовая модель для услуг.
    """

    title = models.CharField(max_length=255, verbose_name='Краткое описание')
    description = models.TextField(verbose_name='Подробное описание', blank=True)
    message = models.TextField(verbose_name='Сообщение покупателю после оплаты', blank=True)
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='%(class)s_services',
        verbose_name='Продавец',
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')
    is_active = models.BooleanField(
        default=True, verbose_name='Активное', help_text='Пометить, если предложение активно'
    )
    orders = GenericRelation(Order)  # Добавляем связь с заказами через GenericForeignKey
    search_description = models.TextField(
        verbose_name='Описание для поиска',
        blank=True,
        help_text='Введите текст, который будет использован для поиска',
    )
    is_auto_delivery = models.BooleanField(
        default=False,
        verbose_name='Автоматическая доставка',
        help_text='Пометить, если услуга поддерживает автоматическую доставку',
    )
    seller_is_online = models.BooleanField(
        default=False,
        verbose_name='Продавец онлайн',
        help_text='Пометить, если продавец находится в сети',
    )

    class Meta:
        abstract = True  # Это базовая модель, она не создаст таблицу в БД.
        ordering = ['-created_at']  # Сортировка по умолчанию: последние записи первыми.
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

    def __str__(self):
        return self.title


class ServiceImage(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    image = models.ImageField(upload_to='service_images/', verbose_name='Загрузить изображение')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Image for {self.content_object}'


class AutoDeliveryFilter(models.Model):
    """
    Базовая модель для услуг, связанных с автовыдачей.
    """

    auto_delivery = models.BooleanField(default=False, verbose_name='Автоматическая выдача')

    class Meta:
        abstract = (
            True  # Эта модель не будет создавать таблицу в базе данных, она только для наследования
        )


class ServerBasedService(BaseService):
    """
    Базовая модель для услуг, связанных с сервером.
    """

    server = models.CharField(
        max_length=50,
        choices=SERVER_CHOICES,
        verbose_name='Сервер',
        default='other',
        help_text='Выберите сервер',
    )

    class Meta:
        abstract = True


class RPService(ServerBasedService, AutoDeliveryFilter):
    """
    Модель услуги для продажи RP (внутриигровой валюты).
    Наследуется от базовой модели BaseService.
    """

    filter_type = models.CharField(
        max_length=50,
        choices=RP_FILTER_CHOICES,
        verbose_name='Тип',
        default='gifts_for_rp',
        help_text='Выберите, к какому фильтру относится эта запись',
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Количество', help_text='Количество валюты в наличии'
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='rp_services', default=1
    )

    class Meta:
        verbose_name = 'Продажа RP'
        verbose_name_plural = 'Продажа RP'

    def __str__(self):
        return f'{self.title} - {self.server} - {self.quantity} доступно'


class AccountService(ServerBasedService, AutoDeliveryFilter):
    """
    Модель услуги для продажи игровых аккаунтов.
    Наследуется от базовой модели BaseService.
    """

    rank = models.CharField(
        max_length=20,
        choices=RANK_CHOICES,
        default='NO_RANK',  # Значение по умолчанию
        verbose_name='Ранг аккаунта',
    )
    filter_type = models.CharField(
        max_length=50,
        choices=ACCOUNT_FILTER_CHOICES,
        verbose_name='Тип фильтра',
        help_text='Выберите, к какому фильтру относится эта запись',
        default='sell',
    )
    images = GenericRelation(ServiceImage, related_query_name='account_service_images')
    skin_count = models.PositiveIntegerField(verbose_name='Количество скинов', default=0)
    account_level = models.PositiveIntegerField(verbose_name='Уровень аккаунта', default=1)
    character_count = models.PositiveIntegerField(verbose_name='Количество персонажей', default=1)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='account_services', default=2
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Количество', help_text='Количество аккаунтов в наличии', default=1
    )

    class Meta:
        verbose_name = 'Продажа аккаунтов'
        verbose_name_plural = 'Продажа аккаунтов'

    def __str__(self):
        return f'{self.title} - {self.server}'


class DonationService(ServerBasedService):
    """
    Модель услуги для доната.
    Наследуется от базовой модели BaseService.
    """

    receiving_method = models.CharField(
        max_length=10,
        choices=RECEIVING_METHOD_CHOICES,
        default='GIFT',  # Значение по умолчанию
        verbose_name='Способ получения',
    )
    filter_type = models.CharField(
        max_length=50,
        choices=DONATION_FILTER_CHOICES,
        verbose_name='Тип фильтра',
        help_text='Выберите, к какому фильтру относится эта запись',
        default='chests',
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='donation_services', default=6
    )
    images = GenericRelation(ServiceImage, related_query_name='donation_service_images')

    class Meta:
        verbose_name = 'Услуга доната'
        verbose_name_plural = 'Услуги доната'

    def __str__(self):
        return f'{self.title} - {self.server}'


class BoostService(ServerBasedService):
    """
    Модель услуги для буста.
    Наследуется от ServerBasedService.
    """

    rank_range = models.CharField(
        max_length=21, choices=RANK_RANGE_CHOICES, default='IRON_BRONZE', verbose_name='Диапазон'
    )
    filter_type = models.CharField(
        max_length=50,
        choices=BOOST_FILTER_CHOICES,
        verbose_name='Тип фильтра',
        help_text='Выберите, к какому фильтру относится эта запись',
        default='default_value',
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='boost_services', default=3
    )

    class Meta:
        verbose_name = 'Услуга буста'
        verbose_name_plural = 'Услуги буста'

    def __str__(self):
        return f'{self.title} - {self.server}'


class GeneralService(BaseService):
    """
    Модель универсальной услуги.
    Наследуется от BaseService.
    """

    filter_type = models.CharField(
        max_length=50,
        choices=GENERAL_FILTER_CHOICES,
        verbose_name='Тип фильтра',
        help_text='Выберите, к какому фильтру относится эта запись',
        default='default_value',
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='general_services', default=7
    )

    class Meta:
        verbose_name = 'Общая услуга'
        verbose_name_plural = 'Общие услуги'

    def __str__(self):
        return self.title


class QualificationService(ServerBasedService):
    """
    Модель услуги квалификации.
    Наследуется от ServerBasedService.
    """

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='qualification_services', default=9
    )

    class Meta:
        verbose_name = 'Услуга квалификации'
        verbose_name_plural = 'Услуги квалификации'

    def __str__(self):
        return f'{self.title} - {self.server}'


class TrainingService(BaseService):
    """
    Модель услуги обучения.
    Наследуется от BaseService.
    """

    filter_type = models.CharField(
        max_length=50,
        choices=TRAINING_FILTER_CHOICES,
        verbose_name='Позиция',
        help_text='Выберите, к какому фильтру относится эта запись',
        default='default_value',
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='training_services', default=4
    )

    class Meta:
        verbose_name = 'Услуга обучения'
        verbose_name_plural = 'Услуги обучения'

    def __str__(self):
        return self.title


class BattlePassService(ServerBasedService):
    """
    Модель услуги по продаже боевого пропуска.
    Наследуется от BaseService.
    """

    filter_type = models.CharField(
        max_length=50,
        choices=BP_FILTER_CHOICES,
        verbose_name='Тип фильтра',
        help_text='Выберите, к какому фильтру относится эта запись',
        default='default_value',
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Количество', help_text='Количество валюты в наличии'
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='battlepass_services', default=5
    )

    class Meta:
        verbose_name = 'Продажа боевого пропуска'
        verbose_name_plural = 'Продажа боевых пропусков'

    def __str__(self):
        return self.title


class OtherService(BaseService, AutoDeliveryFilter):
    """
    Модель услуги для прочих товаров или услуг.
    Наследуется от BaseService.
    """

    filter_type = models.CharField(
        max_length=50,
        choices=OTHER_FILTER_CHOICES,
        verbose_name='Тип фильтра',
        help_text='Выберите, к какому фильтру относится эта запись',
        default='default_value',
    )
    quantity = models.PositiveIntegerField(
        default=1, verbose_name='Количество', help_text='Количество товара/услуги в наличии'
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='other_services', default=8
    )

    class Meta:
        verbose_name = 'Прочее'
        verbose_name_plural = 'Прочее'

    def __str__(self):
        return self.title
