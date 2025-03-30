import logging
from datetime import datetime
from os import getenv
from time import sleep

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.firefox.service import Service

from constants import (
    DATE_FORMAT,
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
    unique_reviews = []  # Инициализируем пустой список для отзывов

    try:
        options = FirefoxOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')  # Для работы с Docker
        options.add_argument('--disable-dev-shm-usage')  # Для работы с Docker
        service = Service(DRIVER_PATH)
        driver = Firefox(service=service, options=options)

        driver.get(org_url)
        sleep(2)
        full_org_url = driver.current_url
        logger.info(f"Полный URL компании: {full_org_url}")
        reviews_url = process_url_twogis(full_org_url)

        # Переходим на страницу с отзывами
        driver.get(reviews_url)
        sleep(4)

        # Считываем HTML страницы с BeautifulSoup после полной загрузки
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        helpful_divs = soup.find_all(lambda tag: (
            tag.name in ("button", "div")
            and "Полезно" in tag.get_text(strip=True)
        ))

        logger.info(f"Найдено {len(helpful_divs)} полезных блоков для обработки")

        for helpful_div in helpful_divs:
            review_container = helpful_div.find_parent("div", class_=TWOGIS_REVIEW_BLOCK)
            if not review_container:
                continue  # Пропускаем, если контейнер не найден

            # Дата, автор, рейтинг и текст отзыва
            date_div = review_container.find('div', class_=TWOGIS_DATE_CLASS)
            review_date = date_div.get_text(strip=True) if date_div else "Дата не найдена"
            actual_date = datetime.now()  # Текущая дата
            review_date = handle_date(review_date, actual_date)

            author_span = review_container.find('span', class_=TWOGIS_AUTHOR_CLASS)
            author_name = author_span.get_text(strip=True) if author_span else "Автор не найден"

            rating_svgs = review_container.find_all('svg', fill=TWOGIS_RATING_COLOR)
            rating_value = len(rating_svgs)

            review_text_a = review_container.select_one(TWOGIS_REVIEW_TEXT_CLASS)
            text = review_text_a.get_text(strip=True) if review_text_a else "Текст не найден"

            # Добавляем уникальные отзывы в список
            review_entry = {
                "review_date": review_date,
                "author_name": author_name,
                "author_link": None,
                "rating_value": rating_value,
                "text": text
            }
            unique_reviews.append(review_entry)

        logger.info(f"Обработано {len(unique_reviews)} уникальных отзывов.")
        return unique_reviews  # Возвращаем список отзывов

    except Exception as e:
        logger.error(f"Ошибка в twogis_check_reviews: {str(e)}")
        return []  # В случае ошибки возвращаем пустой список


def twogis_matching_reviews(org_url):
    """Функция сравнения собранных отзывов с БД."""
    logger.info(f"Запуск проверки совпадений отзывов для URL: {org_url}")

    try:
        # Определяем id ресторана для связи с отзывами
        restaurant_data = read_restaurant_data(rest_data=org_url)
        restaurant_id = restaurant_data['id']
        logger.info(f"Получен id ресторана: {restaurant_id}")

        # Обращаемся в БД к сохранённым отзывам
        old_reviews_data = read_rest_twogis_reviews(
            restaurant_id=restaurant_id
        )

        # Создаём множество отзывов в виде словарей (для быстрого поиска)
        old_reviews_set = set()
        for review in old_reviews_data:
            review_dict = {
                "review_date": review.created_at,
                "author_name": review.author,
                "author_link": review.link,
                "rating_value": review.rating,
                "text": review.content
            }
            old_reviews_set.add(frozenset(review_dict.items()))

        logger.info(f"Найдено {len(old_reviews_set)} старых отзывов в БД.")

        # Собираем последние отзывы на странице ресторана
        new_review_data = twogis_check_reviews(org_url=org_url)

        # Создаём множество для новых уникальных отзывов
        new_reviews_to_semantic = []
        new_reviews_to_save = []

        # Выводим новые отзывы и проверяем, есть ли они среди старых
        for review in new_review_data:
            review_dict = {
                "review_date": review["review_date"],
                "author_name": review["author_name"],
                "author_link": review["author_link"],
                "rating_value": review["rating_value"],
                "text": review["text"]
            }

            logger.debug(f"Обрабатываем отзыв: {review_dict}")

            # Проверяем, если такой отзыв уже есть в старых отзывах
            if frozenset(review_dict.items()) not in old_reviews_set:
                new_reviews_to_semantic.append(review_dict)

        # Выбираем тексты отзывов для формирования семантической оценки
        if new_reviews_to_semantic:
            for new_review in new_reviews_to_semantic:
                semantic = simple_semantic(review_text=new_review["text"])
                new_review["semantic"] = semantic
                new_reviews_to_save.append(new_review)

            logger.info(
                f"Обработано {len(new_reviews_to_save)} отзывов."
            )

        else:
            logger.info("Нет новых отзывов для обработки.")

        # Сортируем и сохраняем новые отзывы
        sorted_new_reviews = []
        if new_reviews_to_save:
            sorted_new_reviews = sorted(
                new_reviews_to_save,
                key=lambda x: datetime.strptime(x["review_date"], DATE_FORMAT)
            )

            for review in sorted_new_reviews:
                logger.info(f"Сохраняем отзыв: {review}")
                review_data_tuple = (
                    restaurant_id,
                    review["review_date"],
                    review["author_name"],
                    review.get("author_link", None),
                    review["rating_value"],
                    review["text"],
                    review["semantic"],
                )

                # Преобразуем кортеж в словарь
                review_data_dict = {
                    'restaurant_id': review_data_tuple[0],
                    'review_date': review_data_tuple[1],
                    'author_name': review_data_tuple[2],
                    'author_link': review_data_tuple[3],
                    'rating_value': review_data_tuple[4],
                    'text': review_data_tuple[5],
                    'semantic': review_data_tuple[6],
                }

                create_twogis_review(review_data_dict)

        else:
            logger.info("Новых отзывов для сохранения не найдено.")

        return sorted_new_reviews

    except Exception as e:
        logger.error(f"Ошибка в twogis_matching_reviews: {str(e)}")
        raise e  # Перебрасываем исключение дальше
