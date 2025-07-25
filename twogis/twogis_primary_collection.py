import logging
from datetime import datetime
from os import getenv
from time import sleep

from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.firefox.service import Service

from constants import (
    DATE_FORMAT,
    TWOGIS_REVIEW_BLOCK,
    TWOGIS_AUTHOR_CLASS,
    TWOGIS_REVIEW_TEXT_CLASS,
    TWOGIS_DATE_CLASS,
)
from data.create_data import create_twogis_review
from utils.date import handle_date
from utils.urls import process_url_twogis
from semantic_analysis.simple_semantic import simple_semantic

load_dotenv()

DRIVER_PATH = getenv('DRIVER_PATH')

# Если тестирую локально. Иначе комментить путь до драйвера ниже.
# DRIVER_PATH = (
#     r'C:\Users\stepa\Downloads\geckodriver-v0.36.0-win64\geckodriver.exe'
# )


# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scroll_to_bottom(driver, elem, prev_reviews_count):
    """Функция для скроллинга до последнего отзыва."""
    driver.execute_script("arguments[0].scrollIntoView();", elem)
    sleep(3)
    reviews = driver.find_elements(By.CLASS_NAME, TWOGIS_REVIEW_BLOCK)

    # Проверяем изменение количества отзывов за три попытки
    attempts = 0
    while attempts < 3:
        if len(reviews) == prev_reviews_count:
            attempts += 1
            logger.info(f"Попытка {attempts}: Количество не изменилось.")
            sleep(1)
            reviews = driver.find_elements(By.CLASS_NAME, TWOGIS_REVIEW_BLOCK)
        else:
            return False  # Отзывы изменились, продолжаем собирать

    # Если три попытки подряд не дали изменений в количестве отзывов, завершаем
    logger.info("Завершаем сбор. Новых отзывов больше нет.")
    return True  # Возвращаем True, что значит, что новых отзывов нет


def twogis_prim_coll(url: str, rest_id: int) -> int:
    logger.info("Запуск сбора отзывов 2ГИС")
    options = FirefoxOptions()
    options.add_argument('--headless')
    service = Service(DRIVER_PATH)
    driver = Firefox(service=service, options=options)
    logger.info("WebDriver запущен")

    reviews_url = process_url_twogis(original_url=url)
    logger.info(f"Ссылка на страницу с отзывами: {reviews_url}")
    driver.get(reviews_url)

    sleep(5)
    logger.info("Ожидание полной загрузки страницы завершено")

    try:
        reviews = driver.find_elements(By.CLASS_NAME, TWOGIS_REVIEW_BLOCK)
        logger.info(f"Начальное количество отзывов: {len(reviews)}")
    except Exception as e:
        logger.error(f"Ошибка при получении начальных отзывов: {e}")
        driver.quit()
        raise

    prev_reviews_count = len(reviews)

    while True:
        try:
            last_review = driver.find_elements(
                By.CLASS_NAME, TWOGIS_REVIEW_BLOCK
            )[-1]
            logger.debug("Получен последний элемент отзывов")
        except IndexError:
            logger.warning("Не найдено ни одного отзыва")
            break

        is_end = scroll_to_bottom(driver, last_review, prev_reviews_count)
        if is_end:
            break
        else:
            reviews = driver.find_elements(By.CLASS_NAME, TWOGIS_REVIEW_BLOCK)
            prev_reviews_count = len(reviews)
            logger.info(
                f"Обновлённое количество отзывов: {prev_reviews_count}"
            )

    # Собираем все уникальные отзывы
    unique_reviews = set()

    for review in reviews:
        try:
            # --- ИЩЕМ ДАТУ ---
            date_div = review.find_element(By.CLASS_NAME, TWOGIS_DATE_CLASS)
            review_date = date_div.text if date_div else "Дата не найдена"
            actual_date = datetime.now()  # Текущая дата
            formatted_date = handle_date(review_date, actual_date)

            # --- ИЩЕМ АВТОРА ---
            author_span = review.find_element(
                By.CLASS_NAME, TWOGIS_AUTHOR_CLASS
            )
            author_name = author_span.text if author_span else "Anon"

            # --- ИЩЕМ РЕЙТИНГ ---
            rating_svgs = review.find_elements(
                By.CSS_SELECTOR, 'svg[fill="#ffb81c"]'
            )
            rating = len(rating_svgs)

            # --- ИЩЕМ ТЕКСТ ОТЗЫВА ---
            review_text_a = review.find_element(
                By.CSS_SELECTOR, TWOGIS_REVIEW_TEXT_CLASS
            )
            review_text_content = (
                review_text_a.text if review_text_a else "Текст не найден"
            )

            # --- ФИЛЬТРАЦИЯ ДУБЛИКАТОВ ---
            review_entry = (
                formatted_date,
                author_name,
                rating,
                review_text_content
            )
            unique_reviews.add(review_entry)

        except Exception as e:
            logger.error(f"Ошибка при обработке отзыва: {e}")
            continue

    # Закрываем браузер
    driver.quit()

    logger.info("Приступаем к запросу семантики отзывов")
    new_reviews_to_save = set()
    for review in unique_reviews:
        semantic = simple_semantic(review_text=review[3])
        # Создаём новый кортеж, добавляя 'semantic' в конец
        review_with_semantic = review + (semantic,)
        new_reviews_to_save.add(review_with_semantic)

    sorted_reviews = sorted(
        new_reviews_to_save,
        key=lambda x: datetime.strptime(x[0], DATE_FORMAT)
    )
    for review in sorted_reviews:
        try:
            # Проверяем наличие обязательных полей
            if not review[0] or not review[3]:
                logger.warning(
                    f"Пропущен отзыв с отсутствующими данными: {review}"
                )
                continue

            review_data = {
                'restaurant_id': rest_id,
                'review_date': review[0],
                'author_name': review[1] if review[1] else 'Аноним',
                'rating_value': review[2],
                'text': review[3],
                'semantic': review[4],
            }
            # Сохраняем отзывы в БД
            create_twogis_review(review_data)
        except Exception as e:
            logger.error(f"Ошибка при добавлении отзыва в базу данных: {e}")

    # Возвращаем число отсортированных отзывов.
    return len(sorted_reviews)
