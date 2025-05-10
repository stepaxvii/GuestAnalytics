import logging
from datetime import datetime
from os import getenv
from time import sleep

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.firefox.service import Service

from constants import (
    TWOGIS_REVIEW_BLOCK,
    TWOGIS_AUTHOR_CLASS,
    TWOGIS_REVIEW_TEXT_CLASS,
    TWOGIS_RATING_COLOR,
    TWOGIS_DATE_CLASS,
)
from data.create_data import create_twogis_review
from data.read_data import read_restaurant_data, read_rest_twogis_reviews
from utils.date import handle_date
from utils.urls import process_url_twogis
from semantic_analysis.simple_semantic import simple_semantic

load_dotenv()

# Настройка логирования
logger = logging.getLogger()

DRIVER_PATH = getenv('DRIVER_PATH')


def twogis_check_reviews(org_url):
    """
    Проверка наличия новых отзывов о ресторане
    и сохранение их в БД.
    """
    logger.info(f"Запуск проверки отзывов для URL: {org_url}")
    unique_reviews = set()  # Используем для хранения уникальных отзывов

    try:
        options = FirefoxOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        service = Service(DRIVER_PATH)
        driver = Firefox(service=service, options=options)

        driver.get(org_url)
        sleep(2)
        full_org_url = driver.current_url
        logger.info(f"Полный URL компании: {full_org_url}")
        reviews_url = process_url_twogis(full_org_url)

        driver.get(reviews_url)
        sleep(4)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        helpful_divs = soup.find_all(lambda tag: (
            tag.name in ("button", "div")
            and "Полезно" in tag.get_text(strip=True)
        ))

        logger.info(
            f"Найдено {len(helpful_divs)} полезных блоков для обработки"
        )

        seen_reviews = set()  # Множество для отслеживания уникальных отзывов

        for helpful_div in helpful_divs:
            review_container = helpful_div.find_parent(
                "div", class_=TWOGIS_REVIEW_BLOCK
            )
            if not review_container:
                continue

            # Извлекаем данные отзыва
            date_div = review_container.find('div', class_=TWOGIS_DATE_CLASS)
            review_date = date_div.get_text(strip=True) if date_div else None

            # Пропускаем отзыв, если дата не была извлечена
            if not review_date:
                logger.error("не удалось найти дату отзыва.")
                continue  # Пропуск отзыва

            # Если дата найдена, обрабатываем её
            review_date = handle_date(review_date, datetime.now())

            author_span = review_container.find(
                'span', class_=TWOGIS_AUTHOR_CLASS
            )
            author_name = author_span.get_text(
                strip=True
            ) if author_span else "Автор не найден"

            rating_svgs = review_container.find_all(
                'svg', fill=TWOGIS_RATING_COLOR
            )
            rating_value = len(rating_svgs)

            review_text_a = review_container.select_one(
                TWOGIS_REVIEW_TEXT_CLASS
            )
            text = review_text_a.get_text(
                strip=True
            ) if review_text_a else "Текст не найден"

            # Создаем уникальный ключ для отзыва
            review_key = (author_name, text, rating_value)

            # Проверяем на дубликат перед добавлением
            if review_key not in seen_reviews:
                seen_reviews.add(review_key)
                unique_reviews.add((
                    review_date,
                    author_name,
                    None,  # author_link
                    rating_value,
                    text
                ))

        driver.quit()
        logger.info(f"Обработано {len(unique_reviews)} уникальных отзывов.")
        return [{
            "review_date": r[0],
            "author_name": r[1],
            "author_link": r[2],
            "rating_value": r[3],
            "text": r[4]
        } for r in unique_reviews]

    except Exception as e:
        logger.error(f"Ошибка в twogis_check_reviews: {str(e)}")
        return []


def twogis_matching_reviews(org_url):
    """Функция сравнения собранных отзывов с БД (без учёта даты)."""
    logger.info(f"Запуск проверки совпадений отзывов для URL: {org_url}")

    try:
        restaurant_data = read_restaurant_data(rest_data=org_url)
        restaurant_id = restaurant_data['id']

        # Загружаем ранее сохранённые отзывы
        old_reviews_data = read_rest_twogis_reviews(
            restaurant_id=restaurant_id
        )
        old_reviews_set = set()

        for review in old_reviews_data:
            review_key = (
                review.author,
                review.content,
                review.rating
            )
            old_reviews_set.add(review_key)

        # Собираем новые отзывы с сайта
        new_review_data = twogis_check_reviews(org_url=org_url)
        new_reviews_to_save = []

        for review in new_review_data:
            review_key = (
                review["author_name"],
                review["text"],
                review["rating_value"]
            )

            if review_key not in old_reviews_set:
                semantic = simple_semantic(review_text=review["text"])
                new_reviews_to_save.append({
                    **review,
                    "semantic": semantic
                })

        if new_reviews_to_save:
            # Сортировка по дате (если нужна для порядка)
            new_reviews_to_save.sort(key=lambda x: x["review_date"])

            for review in new_reviews_to_save:
                review_data = {
                    'restaurant_id': restaurant_id,
                    'review_date': review["review_date"],
                    'author_name': review["author_name"],
                    'author_link': review.get("author_link"),
                    'rating_value': review["rating_value"],
                    'text': review["text"],
                    'semantic': review["semantic"]
                }
                create_twogis_review(review_data)
                logger.info(f"Сохранен отзыв: {review['text'][:50]}...")

        return new_reviews_to_save

    except Exception as e:
        logger.error(f"Ошибка в twogis_matching_reviews: {str(e)}")
        raise
