import logging
from time import sleep
from os import getenv

from dotenv import load_dotenv
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.firefox.service import Service

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

DRIVER_PATH = getenv('DRIVER_PATH')
TG_GROUP = getenv('TG_GROUP')


def check_full_url_yandex(user_url):
    """Функция проверки полной ссылки."""

    logger.info(f"Формируем полный адрес URL по user_url: {user_url}")

    options = FirefoxOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')  # Для работы с Docker
    options.add_argument('--disable-dev-shm-usage')  # Для работы с Docker
    service = Service(DRIVER_PATH)

    try:
        logger.info("Запускаем Firefox WebDriver...")
        driver = Firefox(service=service, options=options)
        logger.info("WebDriver успешно запущен.")
    except Exception as e:
        logger.error(f"Ошибка при запуске WebDriver: {e}")
        return

    driver.get(user_url)
    sleep(1)
    full_org_url = driver.current_url
    logger.info(f"Полный URL компании: {full_org_url}")

    return full_org_url


def process_url_yandex(original_url):
    """Функция форматирования валидного адреса для Яндекса."""

    org_url = original_url.split('?')[0]
    reviews_url = org_url + 'reviews'

    return org_url, reviews_url


def process_url_twogis(original_url):
    """Функция форматирования валидного адреса для 2ГИС."""

    question_mark_index = original_url.find("?")

    if question_mark_index != -1:
        return original_url[:question_mark_index] + "/tab/reviews"

    return original_url + "/tab/reviews"
