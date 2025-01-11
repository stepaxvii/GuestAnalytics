from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from time import sleep
from os import getenv
from dotenv import load_dotenv

from data_base.create_data import create_review
from data_base.read_data import read_some_restaurant_data, read_rest_ya_reviews
from constants import (
    NEW_REVIEWS_SORTED,
    SORTED_BLOCK,
    AUTHOR_ELEMENT,
    DATE_ELEMENT,
    DATE_FORMAT,
    CARD_REVIEWS_BLOCK,
    RATING_ELEMENT,
    TEXT_ELEMENT
)

load_dotenv()

DRIVER_PATH = getenv('DRIVER_PATH', default='')


def ya_check_reviews(org_url):
    """
    Проверка наличия новых отзывов о ресторане
    сохранение их в БД.
    """
    options = FirefoxOptions()
    options.add_argument('--headless')
    service = Service(DRIVER_PATH)
    driver = Firefox(service=service, options=options)

    review_url = org_url + 'reviews'

    # Переходим на страницу с отзывами
    driver.get(review_url)
    sleep(4)

    try:
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
        print("Сортировка по новизне выбрана.")
    except Exception as e:
        print(f"Ошибка при выборе сортировки: {e}")

    # Создаём множество для хранения уникальных отзывов
    unique_reviews = set()
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
            try:
                # Попытка найти значение рейтинга
                rating_value = WebDriverWait(review, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, RATING_ELEMENT)
                    )
                ).get_attribute('content')
            except Exception as e:
                print(f"Ошибка при получении значения рейтинга: {e}")
            text = review.find_element(By.CLASS_NAME, TEXT_ELEMENT).text
            # Сохранение отзыва в множество для уникальности
            review_entry = (
                review_date,
                author_name,
                rating_value,
                text
            )
            unique_reviews.add(review_entry)
            print(f'Уникальных отзывов: {len(unique_reviews)}')

        except Exception as e:
            print(f"Ошибка при получении информации об отзыве: {e}")

    # Закрываем браузер
    driver.quit()
    return unique_reviews


def matching_reviews(org_url):
    """Функция сравнения собранных отзывов с БД."""

    # Определяем id ресторана для связи с отзывами
    restaurant_data = read_some_restaurant_data(org_url=org_url)
    restaurant_id = restaurant_data['id']

    # Обращаемся в БД к последним 50 сохранённым отзывам
    old_review_data = read_rest_ya_reviews(restaurant_id=restaurant_id)[-50:]

    # Создаём множество старых отзывов в виде кортежей (для быстрого поиска)
    old_reviews_set = set()
    for review in old_review_data:
        review_tuple = (
            review.created_at,
            review.author,
            review.rating,
            review.content
        )
        old_reviews_set.add(review_tuple)

    # Собираем последние 50 отзывов на странице ресторана
    new_review_data = ya_check_reviews(org_url=org_url)

    # Создаём множество для новых уникальных отзывов
    new_reviews_to_save = set()

    # Выводим новые отзывы и проверяем, есть ли они среди старых
    for review in new_review_data:
        review_tuple = (
            datetime.strptime(review[0], DATE_FORMAT).date(),
            review[1],
            int(review[2].split('.')[0]),
            review[3]
        )
        if review_tuple not in old_reviews_set:
            new_reviews_to_save.add(review_tuple)

    # Сортировка отзывов по датe
        sorted_new_reviews = sorted(
            new_reviews_to_save,
            key=lambda x: datetime.strptime(x[0], DATE_FORMAT)
        )

    # Если есть новые отзывы, можно их сохранить
    if sorted_new_reviews:
        # Вызываем функцию для сохранения новых отзывов
        for review in sorted_new_reviews:
            # Запись отзыва в базу данных
            review_date, author_name, rating_value, text = review
            review_data = (
                restaurant_id, review_date, author_name, rating_value, text
            )
            create_review(review_data)

    else:
        print("Новых отзывов нет.")

    return sorted_new_reviews
