while True:
        #     try:
        #         # Ожидание появления кнопки "Показать еще"
        #         show_more_button = WebDriverWait(driver, 10).until(
        #             EC.presence_of_element_located((By.XPATH, '//*[@id="news"]/div/div[3]/div[2]'))
        #         )
        #         driver.execute_script("arguments[0].scrollIntoView();", show_more_button)
        #         time.sleep(1)  # Небольшая пауза для плавности
        #         show_more_button.click()
        #         print("Нажата кнопка 'Показать еще'")
        #         # Ожидание прогрузки новостей
        #         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="news"]/div/div[3]/div[2]')))
        #     except NoSuchElementException:
        #         print("Кнопка 'Показать еще' больше не найдена. Все новости загружены.")
        #         break
        #     except ElementClickInterceptedException:
        #         print("Не удалось нажать на кнопку 'Показать еще'. Возможно, блокировка.")
        #         break