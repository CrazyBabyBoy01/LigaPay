from celery import shared_task

from .services import scrape_and_save_news


@shared_task
def update_news_task():
    scrape_and_save_news()
    print('Новости обновлены.')
