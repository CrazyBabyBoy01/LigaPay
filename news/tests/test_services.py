from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from news import services
from news.models import News


User = get_user_model()


from unittest.mock import patch


class TestSaveNews(TestCase):
    """
    Тесты для функции save_news.
    Проверяем только бизнес-логику сохранения и обновления новостей.
    """

    def test_creates_new_news_if_not_exists(self):
        """
        Проверяет, что save_news создаёт новую новость,
        если в базе нет объекта с таким URL.
        """
        article = {
            'title': 'News',
            'description': 'News skins',
            'url': 'https://example.com/1',
            'date': timezone.now(),
            'image': 'https://example.com/image.jpg',
        }
        services.save_news([article])
        self.assertEqual(News.objects.count(), 1)
        news = News.objects.first()
        self.assertEqual(news.title, article['title'])
        self.assertEqual(news.published_at, article['date'])
        self.assertEqual(news.description, article['description'])

    def test_updates_existing_news(self):
        """
        Проверяет, что при повторном вызове save_news
        объект с тем же URL не создаётся заново, а обновляется.
        """
        News.objects.create(
            title='Новость',
            description='Описание',
            url='https://example.com/1',
            published_at=timezone.now(),
            image='https://example.com/image1.jpg',
        )
        article = {
            'title': 'News',
            'description': 'News skins',
            'url': 'https://example.com/1',
            'date': timezone.now(),
            'image': 'https://example.com/image.jpg',
        }
        services.save_news([article])
        self.assertEqual(News.objects.count(), 1)
        news = News.objects.first()
        self.assertEqual(news.title, article['title'])
        self.assertEqual(news.published_at, article['date'])
        self.assertEqual(news.description, article['description'])


class TestScrapeAndSaveNews(TestCase):
    """
    Тесты для функции scrape_and_save_news.
    Используем mocks, чтобы не запускать Selenium и не ходить в интернет.
    """

    @patch('news.services.save_news')
    @patch('news.services.scrape_news')
    def test_calls_save_news_when_scraped_data_is_present(self, mock_scrape, mock_save):
        """
        Если scrape_news возвращает непустой список,
        должна быть вызвана save_news() с этим списком.
        """
        fake_data = [
            {
                'title': 'News',
                'description': 'News skins',
                'url': 'https://example.com/1',
                'date': timezone.now(),
                'image': 'https://example.com/image.jpg',
            }
        ]
        mock_scrape.return_value = fake_data
        services.scrape_and_save_news()
        mock_save.assert_called_once()
        mock_save.assert_called_once_with(fake_data)

    @patch('news.services.save_news')
    @patch('news.services.scrape_news')
    def test_does_not_call_save_news_when_scraped_data_is_empty(self, mock_scrape, mock_save):
        """
        Если scrape_news вернул пустой список,
        save_news() вызываться не должно.
        """
        mock_scrape.return_value = []
        services.scrape_and_save_news()
        mock_save.assert_not_called()

    @patch('news.services.scrape_news')
    def test_logs_exception_when_scrape_news_raises_error(self, mock_scrape):
        """
        Если scrape_news выбрасывает исключение,
        scrape_and_save_news() не должно падать
        и должно записать ошибку в лог (минимум — не кинуть исключение наружу).
        """
        mock_scrape.side_effect = Exception('Ошибка парсинга')
        services.scrape_and_save_news()
