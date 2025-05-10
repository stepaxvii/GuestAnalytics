import logging
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from time import sleep
from os import getenv
from dotenv import load_dotenv
from constants import (
    NEW_REVIEWS_SORTED,
    SORTED_BLOCK,
    AUTHOR_ELEMENT,
    LINK_ELEMENT,
    DATE_ELEMENT,
    DATE_FORMAT,
    CARD_REVIEWS_BLOCK,
    RATING_ELEMENT,
    TEXT_ELEMENT
)
from data.create_data import create_ya_review
from data.read_data import read_restaurant_data, read_rest_ya_reviews
from semantic_analysis.simple_semantic import simple_semantic
from utils.urls import process_url_yandex

load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DRIVER_PATH = getenv('DRIVER_PATH')


def ya_check_reviews(org_url):
    """
    Проверка наличия новых отзывов о ресторане
    и сохранение их в БД.
    """
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
    org_url, reviews_url = process_url_yandex(full_org_url)

    # Переходим на страницу с отзывами
    driver.get(reviews_url)
    sleep(4)

    # Повторение попытки выбора сортировки
    max_attempts = 3  # Максимальное количество попыток
    attempt = 0
    while attempt < max_attempts:
        try:
            attempt += 1
            logging.info(f"Попытка {attempt} из {max_attempts}")

            # Ищем элемент сортировки "По умолчанию" и кликаем по нему
            filter_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CLASS_NAME, SORTED_BLOCK))
            )
            filter_button.click()

            # Ждем, пока появится элемент с опцией "По новизне" и кликаем по нему
            newest_filter = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, NEW_REVIEWS_SORTED))
            )

            # Прокрутка до элемента (если нужно)
            driver.execute_script("arguments[0].scrollIntoView();", newest_filter)

            # Кликаем по элементу "По новизне"
            newest_filter.click()
            logging.info("Сортировка по новизне выбрана.")
            break  # Выход из цикла, если сортировка выбрана успешно
        except Exception as e:
            logging.info(f"Ошибка при выборе сортировки: {e}")
            if attempt == max_attempts:
                logging.error("Не удалось выбрать сортировку после 3 попыток.")
            else:
                sleep(2)  # Небольшая задержка перед повторной попыткой

    # Создаём список для хранения уникальных отзывов
    unique_reviews = []

    # Получаем все элементы с отзывами на странице
    reviews = driver.find_elements(By.CLASS_NAME, CARD_REVIEWS_BLOCK)

    # Сохраняем текущие отзывы из зоны видимости
    for review in reviews:
        try:
            date_str = review.find_element(
                By.CSS_SELECTOR, DATE_ELEMENT
            ).get_attribute('content')
            review_date = datetime.strptime(
                date_str, "%Y-%m-%dT%H:%M:%S.%fZ"
            ).strftime(DATE_FORMAT)
            author_name = review.find_element(
                By.CSS_SELECTOR, AUTHOR_ELEMENT
            ).text
            # Ищем ссылку на пользователя в текущем отзыве
            author_link = 'None'
            try:
                # Используем явное ожидание для ссылки
                author_link = WebDriverWait(review, 5).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, LINK_ELEMENT)
                    )
                ).get_attribute("href")
            except NoSuchElementException as e:
                logging.error(f"Ошибка при поиске ссылки на автора: {e}")
            except Exception as e:
                logging.error(f"Не удалось получить ссылку: {e}")
            try:
                # Попытка найти значение рейтинга
                rating_value = WebDriverWait(review, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, RATING_ELEMENT)
                    )
                ).get_attribute('content')
            except Exception as e:
                logging.info(f"Ошибка при получении значения рейтинга: {e}")
                rating_value = 0

            text = review.find_element(By.CLASS_NAME, TEXT_ELEMENT).text

            # Сохранение отзыва в список для уникальности
            review_entry = {
                "review_date": review_date,
                "author_name": author_name,
                "author_link": author_link,
                "rating_value": rating_value,
                "text": text
            }
            unique_reviews.append(review_entry)

        except Exception as e:
            logging.info(f"Ошибка при получении информации об отзыве: {e}")
    logging.info(f'Уникальных отзывов: {len(unique_reviews)}')

    # Закрываем браузер
    driver.quit()
    return unique_reviews


def ya_matching_reviews(org_url):
    """Функция сравнения собранных отзывов с БД."""

    # Определяем id ресторана для связи с отзывами
    restaurant_data = read_restaurant_data(rest_data=org_url)
    restaurant_id = restaurant_data['id']

    # Обращаемся в БД к сохранённым отзывам
    old_reviews_data = read_rest_ya_reviews(restaurant_id=restaurant_id)

    # Создаём множество старых отзывов в виде словарей (для быстрого поиска)
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

    # Собираем последние 50 отзывов на странице ресторана
    new_review_data = ya_check_reviews(org_url=org_url)

    # Создаём множество для новых уникальных отзывов
    new_reviews_to_semantic = []
    new_reviews_to_save = []

    # Выводим новые отзывы и проверяем, есть ли они среди старых
    for review in new_review_data:
        review_dict = {
            "review_date": review["review_date"],
            "author_name": review["author_name"],
            "author_link": review["author_link"],
            "rating_value": int(
                review["rating_value"].split('.')[0]
            ) if review["rating_value"] else None,
            "text": review["text"]
        }

        # Проверяем, если такой отзыв уже есть в старых отзывах
        if frozenset(review_dict.items()) not in old_reviews_set:
            new_reviews_to_semantic.append(review_dict)

    # Выбираем тексты отзывов для формирования семантической оценки
    if new_reviews_to_semantic:
        for new_review in new_reviews_to_semantic:
            semantic = simple_semantic(review_text=new_review["text"])
            new_review["semantic"] = semantic
            new_reviews_to_save.append(new_review)

    # Инициализируем переменную sorted_new_reviews даже если нет новых отзывов
    sorted_new_reviews = []

    # Если есть новые отзывы, сортируем их по дате и сохраняем
    if new_reviews_to_save:
        sorted_new_reviews = sorted(
            new_reviews_to_save,
            key=lambda x: datetime.strptime(x["review_date"], DATE_FORMAT)
        )

        # Вызываем функцию для сохранения новых отзывов
        for review in sorted_new_reviews:
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

            create_ya_review(review_data_dict)
            logger.info(f"Сохранен отзыв: {review_data_dict['text'][:50]}...")

    else:
        logging.info("Новых отзывов нет.")

    return sorted_new_reviews
