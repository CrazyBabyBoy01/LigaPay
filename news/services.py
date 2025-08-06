import time  # Для задержки
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from .models import News


def scrape_and_save_news():
    driver = webdriver.Chrome()
    login_url = 'https://www.leagueoflegends.com/ru-ru/news/'
    driver.get(login_url)
    try:
        while True:
            try:
                # Ожидание появления кнопки "Показать еще"
                show_more_button = WebDriverWait(driver, 5).until(
                    ec.presence_of_element_located((By.XPATH, '//*[@id="news"]/div/div[3]/div[2]'))
                )
                driver.execute_script('arguments[0].scrollIntoView();', show_more_button)
                time.sleep(1)  # Небольшая пауза для плавности
                show_more_button.click()
                print("Нажата кнопка 'Показать еще'")
                # Ожидание прогрузки новостей
                time.sleep(2)
            except TimeoutException:
                print("Кнопка 'Показать еще' больше не найдена. Все новости загружены.")
                break
            except ElementClickInterceptedException:
                print("Не удалось нажать на кнопку 'Показать еще'. Возможно, блокировка.")
                time.sleep(2)
                continue
        articles = driver.find_elements(By.CLASS_NAME, 'sc-ccb06989-0')
        print(f'Найдено новостей: {len(articles)}')
        for article in articles:
            # print(article.text)
            try:
                title = article.find_element(By.CLASS_NAME, 'sc-ce9b75fd-0').text
                description = article.find_element(By.CLASS_NAME, 'sc-4225abdc-0 ').text
                url = article.get_attribute('href')
                raw_date_published = article.find_element(By.CLASS_NAME, 'sc-bad9cda9-3').text
                image_url = article.find_element(By.CLASS_NAME, 'sc-c8d25c58-0').get_attribute('src')
                # Преобразование даты из 'DD.MM.YYYY' в 'YYYY-MM-DD'
                date_published = datetime.strptime(raw_date_published, '%d.%m.%Y').strftime('%Y-%m-%d')
                if not News.objects.filter(url=url).exists():
                    News.objects.create(
                        title=title,
                        description=description,
                        url=url,
                        date=date_published,
                        image=image_url,
                    )
                    print(f'Сохранена новость: {title}')

            except NoSuchElementException as e:
                print(f'Ошибка при обработке новости: {e}')
    finally:
        driver.quit()
