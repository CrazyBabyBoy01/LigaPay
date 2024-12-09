from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


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

    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание", blank=True)
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="%(class)s_services", verbose_name="Продавец"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    category = models.ForeignKey(to=Category, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")

    class Meta:
        abstract = True  # Это базовая модель, она не создаст таблицу в БД.
        ordering = ["-created_at"]  # Сортировка по умолчанию: последние записи первыми.
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self):
        return self.title


class ServerBasedService(BaseService):
    """
    Базовая модель для услуг, связанных с сервером.
    """

    server = models.CharField(
        max_length=255, verbose_name="Сервер", help_text="Сервер, на котором предоставляется услуга"
    )

    class Meta:
        abstract = True


class RPService(ServerBasedService):
    """
    Модель услуги для продажи RP (внутриигровой валюты).
    Наследуется от базовой модели BaseService.
    """

    quantity = models.PositiveIntegerField(verbose_name="Количество", help_text="Количество валюты в наличии")

    class Meta:
        verbose_name = "Продажа RP"
        verbose_name_plural = "Продажа RP"

    def __str__(self):
        return f"{self.title} - {self.server} - {self.quantity} доступно"


class AccountService(ServerBasedService):
    """
    Модель услуги для продажи игровых аккаунтов.
    Наследуется от базовой модели BaseService.
    """

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
    class Meta:
        verbose_name = "Общая услуга"
        verbose_name_plural = "Общие услуги"

    def __str__(self):
        return self.title


class QualificationService(ServerBasedService):
    """
    Модель услуги квалификации.
    Наследуется от ServerBasedService.
    """
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
    class Meta:
        verbose_name = "Услуга обучения"
        verbose_name_plural = "Услуги обучения"

    def __str__(self):
        return self.title


class BattlePassService(BaseService):
    """
    Модель услуги по продаже боевого пропуска.
    Наследуется от BaseService.
    """
    class Meta:
        verbose_name = "Продажа боевого пропуска"
        verbose_name_plural = "Продажа боевых пропусков"

    def __str__(self):
        return self.title


class OtherService(BaseService):
    """
    Модель услуги для прочих товаров или услуг.
    Наследуется от BaseService.
    """
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Количество",
        help_text="Количество товара/услуги в наличии"
    )

    class Meta:
        verbose_name = "Прочее"
        verbose_name_plural = "Прочее"

    def __str__(self):
        return self.title
