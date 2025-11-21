from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from news.models import News


User = get_user_model()


class TestNewsModel(TestCase):
    """
    Тесты для модели News.
    Проверяем только нашу бизнес-логику, не Django-поля.
    """

    def setUp(self):
        now = timezone.now()
        self.news1 = News.objects.create(
            title='Новость', description='Описание', url='sad', published_at=now
        )

        self.news2 = News.objects.create(
            title='Новость2',
            description='Описание2Описание2Описание2Описание2Описание2Описание2Описание2Описание2Описание2Описание2Описание2Описание2Описание2Описание2Описание2Описание2Описание2Описание2Описание2Описание2Описание2Описание2Описание2Описание2Описание2Описание2',
            url='sad1',
            published_at=now,
        )
        self.news3 = News.objects.create(
            title='Новость', description='Описание', url='sadEW', published_at=now
        )

        News.objects.filter(pk=self.news2.pk).update(published_at=now + timedelta(seconds=30))
        News.objects.filter(pk=self.news3.pk).update(published_at=now + timedelta(seconds=10))

    def test_str_returns_title(self):
        """
        Проверяет, что метод __str__ возвращает title новости.
        """

        self.assertEqual(str(self.news1), self.news1.title)

    def test_short_description_returns_full_text_if_less_than_100(self):
        """
        Проверяет, что short_description возвращает текст без изменений,
        если длина description меньше или равна 100 символов.
        """
        result = self.news1.short_description()
        self.assertEqual(result, 'Описание')

    def test_short_description_truncates_text_if_more_than_100(self):
        """
        Проверяет, что short_description возвращает первые 100 символов
        и добавляет '...', если длина description больше 100 символов.
        """
        result = self.news2.short_description()
        self.assertEqual(
            result,
            'Описание2Описание2Описание2Описание2Описание2Описание2Описание2Описание2Описание2Описание2Описание2О...',
        )

    def test_news_ordering_by_published_at_desc(self):
        """
        Опционально: проверяет, что Meta.ordering сортирует новости по published_at убыванию.
        Тестируем только если это важная бизнес-логика выбора порядка отображения.
        """
        result = News.objects.all()
        self.assertEqual(result[0], self.news2)
        self.assertEqual(result[1], self.news3)
        self.assertEqual(result[2], self.news1)
