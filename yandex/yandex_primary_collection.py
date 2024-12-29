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

load_dotenv()

DRIVER_PATH = getenv('DRIVER_PATH', default='')
validated_url = 'https://yandex.ru/maps/org/sorrento/134452148915/reviews/'


def ya_prim_coll(org_url, reviews_url):
    options = FirefoxOptions()
    options.add_argument('--headless')
    service = Service(DRIVER_PATH)
    driver = Firefox(service=service, options=options)
    actions = ActionChains(driver)

    # Определяем текущую дату
    actual_date = datetime.now().strftime("%Y-%m-%d")
    print(actual_date)

    # Переходим на страницу с отзывами и ждём полной загрузки
    driver.get(org_url)
    sleep(5)

    # Получаем название организации
    org_name_element = driver.find_element(
        By.CSS_SELECTOR, 'h1.orgpage-header-view__header'
    )
    org_name = org_name_element.text.strip()

    # Получаем полный адрес
    address_element = driver.find_element(
        By.CLASS_NAME, 'orgpage-header-view__address'
    )
    full_address = address_element.text.strip()

    print(f"Название организации: {org_name}")
    print(f"Полный адрес: {full_address}")

    # Переходим на страницу с отзывами и ждём полной загрузки
    driver.get(reviews_url)
    sleep(5)

    total_count_element = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located(
            (By.CLASS_NAME, 'card-section-header__title')
        )
    )
    total_count_text = total_count_element.text
    total_count = int(total_count_text.split()[0])
    print(f"Общее количество отзывов: {total_count}")
    sleep(2)
    with open("ya_docs.txt", "w", encoding='utf-8') as file:
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
                        review_date, 'yandex', author_name, rating_value, text)
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

        # Запись уникальных отзывов в файл после завершения сбора данных
        for review in sorted_reviews:
            file.write(f"{review}\n")

    # Закрываем браузер
    driver.quit()
    return total_count
