import logging
import time
from datetime import datetime

from django.utils.timezone import make_aware
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from .models import News


logger = logging.getLogger(__name__)


def scrape_news():
    """Возвращает список новостей в виде словарей"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get('https://www.leagueoflegends.com/ru-ru/news/')
    articles_data = []

    try:
        max_clicks = 50
        clicks = 0

        while clicks < max_clicks:
            try:
                show_more_button = WebDriverWait(driver, 5).until(
                    ec.element_to_be_clickable((By.CLASS_NAME, 'cta'))
                )
                driver.execute_script('arguments[0].scrollIntoView(true);', show_more_button)
                time.sleep(0.5)
                driver.execute_script('arguments[0].click();', show_more_button)
                logger.info(f"Нажата кнопка 'Показать больше' ({clicks + 1}/{max_clicks})")
                WebDriverWait(driver, 10).until(
                    ec.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, '[data-testid="articlefeaturedcard-component"]')
                    )
                )
                clicks += 1

            except TimeoutException:
                logger.info("Кнопка 'Показать еще' больше не найдена. Все новости загружены.")
                break
            except ElementClickInterceptedException:
                logger.warning("Не удалось нажать на кнопку 'Показать еще'. Пробую снова...")
                time.sleep(2)
                continue

        articles = driver.find_elements(By.CSS_SELECTOR, '[data-testid="articlefeaturedcard-component"]')
        logger.info(f'Найдено новостей: {len(articles)}')

        for article in articles:
            try:
                title = article.find_element(By.CSS_SELECTOR, '[data-testid="card-title"]').text
                try:
                    description = article.find_element(
                        By.CSS_SELECTOR, '[data-testid="card-description"]'
                    ).text
                except NoSuchElementException:
                    description = ''
                url = article.get_attribute('href')

                time_element = article.find_element(By.CSS_SELECTOR, '[data-testid="card-date"] time')
                raw_date = time_element.get_attribute('datetime')

                date_published = make_aware(datetime.strptime(raw_date, '%Y-%m-%dT%H:%M:%S.%fZ'))

                image_url = article.find_element(
                    By.CSS_SELECTOR, '[data-testid="card-image"] img'
                ).get_attribute('src')

                articles_data.append(
                    {
                        'title': title,
                        'description': description,
                        'url': url,
                        'date': date_published,
                        'image': image_url,
                    }
                )

            except NoSuchElementException as e:
                logger.error(f'Ошибка при обработке новости: {e}')
                continue

    finally:
        driver.quit()

    logger.info(f'Всего собрано новостей: {len(articles_data)}')
    return articles_data


def save_news(articles_data):
    """Сохраняет или обновляет новости в базе"""
    for article in articles_data:
        obj, created = News.objects.update_or_create(
            url=article['url'],
            defaults={
                'title': article['title'],
                'description': article['description'],
                'published_at': article['date'],
                'image': article['image'],
            },
        )
        if created:
            logger.info(f'Добавлена новость: {obj.title}')
        else:
            logger.info(f'Обновлена новость: {obj.title}')


def scrape_and_save_news():
    """Основная точка входа для парсинга и сохранения новостей"""
    try:
        articles = scrape_news()
        if articles:
            save_news(articles)
            logger.info(f'Успешно обработано {len(articles)} новостей.')
        else:
            logger.info('Новых новостей не найдено.')
    except Exception as e:
        logger.exception(f'Ошибка при выполнении парсинга новостей: {e}')
