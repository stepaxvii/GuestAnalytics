import re
import logging
from os import getenv
from time import sleep

from dotenv import load_dotenv
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


load_dotenv()

# Настройки драйвера и пути
DRIVER_PATH = getenv('DRIVER_PATH', default='')
validated_url = 'https://2gis.ru/krasnodar/firm/70000001095624348/tab/reviews'

review_block = '_1k5soqfl'
author_class = '_16s5yj36'
review_text_class = '_h3pmwn'
rating_class = '_1fkin5c'
date_class = '_139ll30'


def twogis_valid_content(url):
    """Функция для определения необходимых для парсинга контейнеров."""
    options = FirefoxOptions()
    # options.add_argument('--headless')
    service = Service(DRIVER_PATH)
    driver = Firefox(service=service, options=options)

    # Открываем страницу
    driver.get(url)
    sleep(5)

    review_text = ""
    author_name = ""
    rating_percentage = ""
    review_date = ""

    try:
        # Находим кнопку "Полезно" (кнопка, которая есть на странице)
        useful_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//button[.//div[text()="Полезно"]]'))
        )

        # Находим блок отзыва для кнопки "Полезно"
        review_block = useful_button.find_element(
            By.XPATH, './ancestor::div[contains(@class, "_1k5soqfl")]')

        # Ищем имя автора
        try:
            author_element = review_block.find_element(
                By.XPATH, './/span[@class="_14quei"]//span[@class="_16s5yj36"]')
            author_name = author_element.text.strip() if author_element else "Не указано"
        except Exception as e:
            logging.error(f"Не удалось найти автора: {e}")
            author_name = "Не указано"

        # Ищем текст отзыва
        try:
            review_text_element = review_block.find_element(By.XPATH, './/a[@class="_1oir7fah"]')
            review_text = review_text_element.text.strip() if review_text_element else "Отзыв не найден"
        except Exception as e:
            logging.error(f"Не удалось найти текст отзыва: {e}")
            review_text = "Отзыв не найден"

        # Ищем блок со звездами (для рейтинга)
        try:
            rating_container = review_block.find_element(
                By.XPATH, './/div[contains(@style, "width")]')
            rating_style = rating_container.get_attribute("style")
            rating_percentage = rating_style.split("width:")[1].split("%")[0].strip() if "width" in rating_style else "Не указан"
        except Exception as e:
            logging.error(f"Не удалось найти рейтинг: {e}")
            rating_percentage = "Не указан"

        # Ищем дату отзыва (попробуем искать по шаблону даты)
        try:
            # Поиск по всем блокам с текстом, который может содержать дату
            date_elements = review_block.find_elements(By.XPATH, './/div[contains(text(), "янв") or contains(text(), "фев")]')
            # Используем регулярные выражения, чтобы вычленить дату
            for date_elem in date_elements:
                date_text = date_elem.text.strip()
                if re.match(r'\d{1,2}\s[а-яА-Я]+\s\d{4}', date_text):  # Шаблон для даты в формате "01 янв 2025"
                    review_date = date_text
                    break
            else:
                review_date = "Дата не указана"
        except Exception as e:
            logging.error(f"Не удалось найти дату: {e}")
            review_date = "Дата не указана"

    except Exception as e:
        logging.error(f"Ошибка при обработке страницы: {e}")
    finally:
        driver.quit()

    return {
        'review': review_text,
        'author': author_name,
        'content': review_text,
        'rating': rating_percentage,
        'date': review_date
    }


print(twogis_valid_content(validated_url))
