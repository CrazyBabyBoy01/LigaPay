# import time  # Для задержки

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys


# driver = webdriver.Chrome()
# login_url = 'https://www.leagueoflegends.com/en-gb/news/'
# driver.get(login_url)

# #извлечь статистику
# stats_table= driver.find_element(By.CLASS_NAME, 'sc-1de19c4d-0')
# print(stats_table.text)


class ContextMixin:
    title = 'LigaPay'
    background_image = None
    subtitle = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['background_image'] = self.background_image
        context['subtitle'] = self.subtitle
        return context

