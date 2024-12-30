from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
from time import sleep
from os import getenv
from dotenv import load_dotenv
from selenium.common.exceptions import NoSuchElementException

from data_base.create_data import create_restaurant, create_review
from data_base.read_data import read_restaurant_data
from utils.urls import process_url_yandex

load_dotenv()

DRIVER_PATH = getenv('DRIVER_PATH', default='')
validated_url = 'https://yandex.ru/maps/org/sorrento/134452148915/reviews/'


def ya_prim_coll(original_url):
    options = FirefoxOptions()
    options.add_argument('--headless')
    service = Service(DRIVER_PATH)
    driver = Firefox(service=service, options=options)
    actions = ActionChains(driver)

    # Определяем текущую дату
    actual_date = datetime.now().strftime("%Y-%m-%d")
    print(actual_date)

    # Переходим на url юзера
    driver.get(original_url)
    sleep(2)

    # Извлекаем полный url-адрес для дальнейшей работы
    full_org_url = driver.current_url

    org_url, reviews_url = process_url_yandex(full_org_url)

    # Переходим на страницу компании и ждём полной загрузки
    driver.get(org_url)
    sleep(5)

    # Получаем название организации с обработкой ошибок
    try:
        org_name_element = driver.find_element(By.CSS_SELECTOR, 'h1.orgpage-header-view__header')
        org_name = org_name_element.text.strip()
    except NoSuchElementException:
        org_name = None
        print("Не удалось найти название организации")

    # Получаем полный адрес с обработкой ошибок
    try:
        address_element = driver.find_element(By.CLASS_NAME, 'orgpage-header-view__address')
        full_address = address_element.text.strip()
    except NoSuchElementException:
        full_address = None
        print("Не удалось найти полный адрес")

    # Проверяем, что данные получены перед сохранением в базу данных
    if org_name is not None:
        # Формирование общей информации о ресторане
        restaurant_data = (org_name, org_url, full_address)
        try:
            create_restaurant(data=restaurant_data)
        except Exception as e:
            print(f"Ошибка при добавлении ресторана в базу данных: {e}")
    else:
        print("Пропускаем ресторан, так как название не найдено")

    # Переходим на страницу с отзывами и ждём полной загрузки
    driver.get(reviews_url)
    sleep(5)

    # Вычисляем общее количество отзывов
    total_count_element = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located(
            (By.CLASS_NAME, 'card-section-header__title')
        )
    )
    total_count_text = total_count_element.text
    total_count = int(total_count_text.split()[0])
    print(f"Общее количество отзывов: {total_count}")
    sleep(2)

    # Создаём текстовый документ для хранения и отправки отзывов юзеру
    doc_reviews = f"Отзывы {org_name}.txt"
    with open(doc_reviews, "w", encoding='utf-8') as file:
        unsuccessful_attempts = 0
        unique_reviews = set()

        while unsuccessful_attempts < 3 and len(unique_reviews) < total_count:
            # Получаем все отзывы на странице после прокрутки
            reviews = driver.find_elements(
                By.CLASS_NAME, 'business-review-view'
            )

            # Сохраняем текущие отзывы из зоны видимости
            for review in reviews:
                try:
                    date_str = review.find_element(
                        By.CSS_SELECTOR, 'meta[itemprop="datePublished"]'
                    ).get_attribute('content')
                    review_date = datetime.strptime(
                        date_str, "%Y-%m-%dT%H:%M:%S.%fZ"
                    ).strftime("%Y-%m-%d")
                    author_name = review.find_element(
                        By.CSS_SELECTOR,
                        'div.business-review-view__author-name '
                        'span[itemprop="name"]'
                    ).text
                    try:
                        # Попытка найти значение рейтинга
                        rating_value = WebDriverWait(review, 10).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR,
                                    'span[itemprop="reviewRating"] '
                                    'meta[itemprop="ratingValue"]')
                            )
                        ).get_attribute('content')
                    except Exception as e:
                        print(f"Ошибка при получении значения рейтинга: {e}")
                    text = review.find_element(
                        By.CLASS_NAME, 'business-review-view__body-text'
                    ).text
                    # Сохранение отзыва в множество для уникальности
                    review_entry = (
                        review_date, author_name, rating_value, text)
                    unique_reviews.add(review_entry)
                    print(f'Уникальных отзывов: {len(unique_reviews)}')

                except Exception as e:
                    print(f"Ошибка при получении информации об отзыве: {e}")

            for i in range(0, 30):
                # Прокрутка страницы вниз для получения следующего отзыва
                actions.scroll_by_amount(0, 2000).perform()
                sleep(0.5)

        # Сортировка отзывов по дате в порядке убывания
        sorted_reviews = sorted(
            unique_reviews,
            key=lambda x: datetime.strptime(x[0], '%Y-%m-%d'),
            reverse=True
        )

        # Определяем id ресторана для связи с отзывами
        restaurant_id = read_restaurant_data(org_url=org_url)[0]

        # Запись уникальных отзывов в файл после завершения сбора данных
        for review in sorted_reviews:
            file.write(f"{review}\n")

            # Запись отзыва в базу данных
            review_date, author_name, rating_value, text = review
            review_data = (
                restaurant_id, review_date, author_name, rating_value, text
            )
            create_review(review_data)

    # Закрываем браузер
    driver.quit()
    return total_count, doc_reviews
