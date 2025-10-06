import time

from django.core.management.base import BaseCommand

from news.services import scrape_and_save_news


class Command(BaseCommand):
    help = 'Парсит новости с официального сайта League of Legends и сохраняет их в базу данных.'

    def handle(self, *args, **options):
        start = time.time()
        self.stdout.write(self.style.MIGRATE_HEADING('Запуск парсинга новостей...'))

        try:
            scrape_and_save_news()
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Ошибка при парсинге: {e}'))
        else:
            duration = time.time() - start
            self.stdout.write(self.style.SUCCESS(f'Парсинг завершён успешно за {duration:.2f} сек'))
