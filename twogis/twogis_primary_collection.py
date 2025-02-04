import logging
from datetime import datetime
from os import getenv
from time import sleep

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.firefox.service import Service

from constants import (
    TWOGIS_REVIEW_BLOCK,
    TWOGIS_AUTHOR_CLASS,
    TWOGIS_REVIEW_TEXT_CLASS,
    TWOGIS_RATING_COLOR,
    TWOGIS_DATE_CLASS,
)
from utils.date import handle_date

load_dotenv()
logging.basicConfig(level=logging.INFO)

DRIVER_PATH = getenv('DRIVER_PATH', default='')

# Логирование
logging.basicConfig(level=logging.INFO)


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
            logging.info(f"Попытка {attempts}: Количество не изменилось.")
            sleep(1)
            reviews = driver.find_elements(By.CLASS_NAME, TWOGIS_REVIEW_BLOCK)
        else:
            return False  # Отзывы изменились, продолжаем собирать

    # Если три попытки подряд не дали изменений в количестве отзывов, завершаем
    logging.info("Завершаем сбор. Новых отзывов больше нет.")
    return True  # Возвращаем True, что значит, что новых отзывов нет


def twogis_prim_coll(url):
    options = FirefoxOptions()
    options.add_argument('--headless')
    service = Service(DRIVER_PATH)
    driver = Firefox(service=service, options=options)
    driver.get(url)

    # Подождём, пока страница полностью загрузится
    sleep(5)

    # Считываем начальное количество отзывов
    reviews = driver.find_elements(By.CLASS_NAME, TWOGIS_REVIEW_BLOCK)
    prev_reviews_count = len(reviews)

    # Прокручиваем страницу и собираем новые отзывы
    while True:
        # Получаем последний элемент отзывов
        last_review = driver.find_elements(
            By.CLASS_NAME, TWOGIS_REVIEW_BLOCK
        )[-1]
        is_end = scroll_to_bottom(driver, last_review, prev_reviews_count)
        if is_end:
            break
        else:
            reviews = driver.find_elements(By.CLASS_NAME, TWOGIS_REVIEW_BLOCK)
            prev_reviews_count = len(reviews)

    # Считываем HTML страницы с BeautifulSoup после полной загрузки
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Собираем все уникальные отзывы
    unique_reviews = set()

    helpful_divs = soup.find_all(lambda tag: (
        tag.name in ("button", "div") and "Полезно" in tag.get_text(strip=True)
    ))

    for helpful_div in helpful_divs:
        review_container = helpful_div.find_parent(
            "div", class_=TWOGIS_REVIEW_BLOCK
        )
        if not review_container:
            continue  # Пропускаем, если контейнер не найден

        # --- ИЩЕМ ДАТУ ---
        date_div = review_container.find('div', class_=TWOGIS_DATE_CLASS)
        review_date = date_div.get_text(
            strip=True
        ) if date_div else "Дата не найдена"
        actual_date = datetime.now()  # Текущая дата
        formatted_date = handle_date(review_date, actual_date)

        # --- ИЩЕМ АВТОРА ---
        author_span = review_container.find(
            'span', class_=TWOGIS_AUTHOR_CLASS
        )
        author_name = author_span.get_text(
            strip=True
        ) if author_span else "Автор не найден"

        # --- ИЩЕМ РЕЙТИНГ ---
        rating_svgs = review_container.find_all(
            'svg', fill=TWOGIS_RATING_COLOR
        )
        rating = len(rating_svgs)

        # --- ИЩЕМ ТЕКСТ ОТЗЫВА ---
        review_text_a = review_container.select_one(TWOGIS_REVIEW_TEXT_CLASS)
        review_text_content = review_text_a.get_text(
            strip=True
        ) if review_text_a else "Текст не найден"

        # --- ФИЛЬТРАЦИЯ ДУБЛИКАТОВ ---
        review_entry = (
            formatted_date, author_name, rating, review_text_content
        )
        unique_reviews.add(review_entry)

    # Закрываем браузер
    driver.quit()

    # Возвращаем все уникальные отзывы
    results = [
        {
            "date": review[0],
            "author": review[1],
            "rating": review[2],
            "text": review[3]
        }
        for review in unique_reviews
    ]

    return results


if __name__ == "__main__":
    url = "https://2gis.ru/sochi/firm/70000001082615141/tab/reviews"
    results = twogis_prim_coll(url)

    for r in results:
        print(r)
    print(len(results))
