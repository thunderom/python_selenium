import pytest

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# базовая фикстура
@pytest.fixture(scope = 'session')
def browser():
	# описываем опции запуска браузера
    CHROME_OPTIONS = Options()
    CHROME_OPTIONS.add_argument("--no-sandbox")             # запускаем Chrome без "песочницы"
    # CHROME_OPTIONS.add_argument("start-maximized")        # открываем на полный экран
    CHROME_OPTIONS.add_argument("window-size=1920,1080")    # устанавливаем размер окна
    CHROME_OPTIONS.add_argument("--disable-infobars")       # отключаем инфо сообщения
    CHROME_OPTIONS.add_argument("--disable-extensions")     # отключаем расширения
    CHROME_OPTIONS.add_argument("--disable-gpu")            # отключаем использование GPU
    CHROME_OPTIONS.add_argument("--disable-dev-shm-usage")  # отключаем использование разделяемой памяти
    CHROME_OPTIONS.add_argument("--headless")               # спец. режим "без браузера"
	
	# устанавливаем webdriver в соответствии с версией используемого браузера
    SERVICE = Service()

    # запускаем браузер с указанными выше настройками
    DRIVER = webdriver.Chrome(service = SERVICE, options = CHROME_OPTIONS)
    
    # передаём объект DRIVER в тестовую функцию
    yield DRIVER

    # закрываем браузер после выполнения теста
    DRIVER.quit()
