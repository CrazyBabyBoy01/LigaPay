import time  # Для задержки
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .models import News


def scrape_and_save_news():
    driver = webdriver.Chrome()
    login_url = "https://www.leagueoflegends.com/ru-ru/news/"
    driver.get(login_url)
    news_data = []
    try:
        while True:
            try:
                # Ожидание появления кнопки "Показать еще"
                show_more_button = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="news"]/div/div[3]/div[2]'))
                )
                driver.execute_script("arguments[0].scrollIntoView();", show_more_button)
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
        articles = driver.find_elements(By.CLASS_NAME, "sc-ccb06989-0")
        print(f"Найдено новостей: {len(articles)}")
        for article in articles:
            # print(article.text)
            try:
                title = article.find_element(By.CLASS_NAME, "sc-ce9b75fd-0").text
                description = article.find_element(By.CLASS_NAME, "sc-4225abdc-0 ").text
                url = article.get_attribute("href")
                raw_date_published = article.find_element(By.CLASS_NAME, "sc-bad9cda9-3").text
                image_url = article.find_element(By.CLASS_NAME, "sc-c8d25c58-0").get_attribute("src")
                # Преобразование даты из 'DD.MM.YYYY' в 'YYYY-MM-DD'
                date_published = datetime.strptime(raw_date_published, "%d.%m.%Y").strftime("%Y-%m-%d")
                if not News.objects.filter(url=url).exists():
                    News.objects.create(
                        title=title,
                        description=description,
                        url=url,
                        date=date_published,
                        image=image_url,
                    )
                    print(f"Сохранена новость: {title}")

            except NoSuchElementException as e:
                print(f"Ошибка при обработке новости: {e}")
    finally:
        driver.quit()
    # WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "sc-ccb06989-0")))
    # # Поиск всех блоков новостей
    # articles = driver.find_elements(By.CLASS_NAME, "sc-ccb06989-0")
    # print(f"Найдено новостей: {len(articles)}")
    # for article in articles:
    #     # print(article.text)

    #     # Заголовок
    #     title = article.find_element(By.CLASS_NAME, "sc-ce9b75fd-0").text
    #     # Описание
    #     try:
    #         description = article.find_element(By.CLASS_NAME, "sc-4225abdc-0 ").text
    #     except NoSuchElementException:
    #         description = "Описание отсутствует"

    #     try:
    #         url = article.get_attribute("href")
    #     except NoSuchElementException:
    #         description = "Ссылка отсутствует"

    #     # Ссылка на новость
    #     # url = article.find_element(By.CLASS_NAME, "sc-ccb06989-0").get_attribute("href")
    #     # print(3)
    #     # Дата публикации
    #     try:
    #         date_published = article.find_element(By.XPATH, ".//time").text
    #     except NoSuchElementException:
    #         date_published = "Дата отсутствует"

    #     # URL изображения
    #     try:
    #         image_url = article.find_element(By.CLASS_NAME, "sc-c8d25c58-0").get_attribute("src")
    #     except NoSuchElementException:
    #         image_url = "URL изображения отсутствует"

    #     # Добавление данных в список
    #     news_data.append(
    #         {
    #             "title": title,
    #             "description": description,
    #             "url": url,
    #             "date_published": date_published,
    #             "image_url": image_url,
    #         }
    #     )

    # return news_data


# if __name__ == "__main__":
#     news = scrape_news()
#     print(news)
