import logging

from celery import shared_task

from .services import scrape_and_save_news


logger = logging.getLogger(__name__)


@shared_task
def scrape_news_task():
    """
    Асинхронная задача для парсинга и обновления новостей.

    Запускается через Celery Beat (по расписанию).
    Использует функцию `scrape_and_save_news` из services.py.
    """
    logger.info('Запуск задачи scrape_news_task через Celery Beat')
    scrape_and_save_news()
    logger.info('Задача scrape_news_task завершена')
