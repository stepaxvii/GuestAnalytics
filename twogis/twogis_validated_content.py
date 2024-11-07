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
# Логирование
logging.basicConfig(level=logging.INFO)

# Настройки драйвера и пути
DRIVER_PATH = getenv('DRIVER_PATH', default='')
validated_url = 'https://2gis.ru/sochi/firm/70000001067211531/tab/reviews'

options = FirefoxOptions()
service = Service(DRIVER_PATH)
driver = Firefox(service=service, options=options)

# Открываем страницу
logging.info("Открываем страницу с отзывами...")
driver.get(validated_url)
sleep(5)

try:
    # Находим кнопку "Полезно"
    useful_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//button[.//div[text()="Полезно"]]'))
    )
    logging.info('Кнопка "Полезно" найдена!')

    # Находим блок отзыва для кнопки "Полезно"
    review_block = useful_button.find_element(By.XPATH, './ancestor::div[contains(@class, "_1k5soqfl")]')
    logging.info("Определяем блок отзыва для кнопки 'Полезно'...")

    # Ищем имя автора
    logging.info("Ищем контейнер с именем автора...")
    author_element = review_block.find_element(By.XPATH, './/span[contains(@title, "")]')
    author_class = author_element.get_attribute("class")
    logging.info(f"Класс контейнера с именем автора: {author_class}")

    # Ищем текст отзыва
    logging.info("Ищем контейнер с текстом отзыва...")
    review_text_element = review_block.find_element(By.XPATH, './/a')
    review_text_class = review_text_element.get_attribute("class")
    logging.info(f"Класс контейнера с текстом отзыва: {review_text_class}")

    # Ищем блок со звездами через позицию относительно текста отзыва или автора
    logging.info("Ищем контейнер с рейтингом на основе положения относительно текста отзыва...")
    rating_container = review_block.find_element(By.XPATH, './/div[contains(@style, "width")]')
    rating_class = rating_container.get_attribute("class")
    logging.info(f"Класс контейнера с рейтингом: {rating_class}")

    # Ищем контейнер с датой по отношению к кнопке "Полезно"
    logging.info("Ищем контейнер с датой...")
    date_element = review_block.find_element(By.XPATH, './/div[not(@class="") and contains(text(), " ")]')
    date_class = date_element.get_attribute("class")
    logging.info(f"Класс контейнера с датой: {date_class}")

except Exception as e:
    logging.error(f"Ошибка при определении классов контейнеров: {e}")
finally:
    driver.quit()
