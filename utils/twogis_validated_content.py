from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from time import sleep
from os import getenv
from dotenv import load_dotenv

load_dotenv()

# Настройки драйвера и пути
DRIVER_PATH = getenv('DRIVER_PATH', default='')
validated_url = 'https://2gis.ru/sochi/firm/70000001067211531/tab/reviews'


def twogis_valid_content(url):
    """Функция для определения необходимых для парсинга контейнеров."""
    options = FirefoxOptions()
    options.add_argument('--headless')
    service = Service(DRIVER_PATH)
    driver = Firefox(service=service, options=options)

    # Открываем страницу
    driver.get(url)
    sleep(5)

    try:
        # Находим кнопку "Полезно"
        useful_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//button[.//div[text()="Полезно"]]'))
        )

        # Находим блок отзыва для кнопки "Полезно"
        review_block = useful_button.find_element(
            By.XPATH, './ancestor::div[contains(@class, "_1k5soqfl")]')

        # Ищем имя автора
        author_element = review_block.find_element(
            By.XPATH, './/span[contains(@title, "")]')
        author_class = author_element.get_attribute("class")

        # Ищем текст отзыва
        review_text_element = review_block.find_element(By.XPATH, './/a')
        review_text_class = review_text_element.get_attribute("class")

        # Ищем блок со звездами через позицию относительно текста или автора
        rating_container = review_block.find_element(
            By.XPATH, './/div[contains(@style, "width")]')
        rating_class = rating_container.get_attribute("class")

        # Ищем контейнер с датой по отношению к кнопке "Полезно"
        date_element = review_block.find_element(
            By.XPATH, './/div[not(@class="") and contains(text(), " ")]')
        date_class = date_element.get_attribute("class")
    except Exception as e:
        logging.error(f"Ошибка при определении классов контейнеров: {e}")
    finally:
        driver.quit()

    return (
        review_block,
        author_class,
        review_text_class,
        rating_class,
        date_class
    )


# print(twogis_valid_content(validated_url))
