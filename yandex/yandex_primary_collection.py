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
    POZITIVE_REVIEWS_SORTED,
    NEGATIVE_REVIEWS_SORTED,
    NEW_REVIEWS_SORTED,
    DEFAULT_REVIEWS_SORTED,
    SORTED_BLOCK,
    ORG_NAME_BLOCK,
    ORG_ADDRESS_BLOCK,
    AUTHOR_ELEMENT,
    DATE_ELEMENT,
    DATE_FORMAT,
    COUNT_REVIEWS_BLOCK,
    LINK_ELEMENT,
    CARD_REVIEWS_BLOCK,
    RATING_ELEMENT,
    TEXT_ELEMENT,
    MAX_VIEW_REVIEWS
)
from data_base.create_data import create_restaurant, create_review
from data_base.read_data import read_some_restaurant_data
# from semantic_analysis.simple_semantic import simple_semantic
from utils.urls import process_url_yandex

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

DRIVER_PATH = getenv('DRIVER_PATH')


def scroll_to_bottom(driver, elem, prev_reviews_count):
    """Функция для скроллинга до последнего отзыва."""
    driver.execute_script("arguments[0].scrollIntoView();", elem)
    sleep(3)
    reviews = driver.find_elements(By.CLASS_NAME, CARD_REVIEWS_BLOCK)

    # Проверяем изменение количества отзывов за три попытки
    attempts = 0
    while attempts < 3:
        if len(reviews) == prev_reviews_count:
            attempts += 1
            logger.info(f"Попытка {attempts}: Количество не изменилось.")
            sleep(1)
            reviews = driver.find_elements(By.CLASS_NAME, CARD_REVIEWS_BLOCK)
        else:
            return False  # Отзывы изменились, продолжаем собирать

    # Если три попытки подряд не дали изменений в количестве отзывов, завершаем
    logger.info("Завершаем сбор.")
    return True  # Возвращаем True, что значит, что новых отзывов нет


# def ya_prim_coll(original_url):
#     """
#     Функция для первичного сбора отзывов ресторана
#     и заполнения БД данными о ресторане и отзывами.
#     """
#     logger.info(f"Начинаем сбор данных с URL: {original_url}")

#     options = FirefoxOptions()
#     options.add_argument('--headless')
#     service = Service(DRIVER_PATH)

#     # Инициализация драйвера Firefox
#     try:
#         logger.info("Запускаем Firefox WebDriver...")
#         driver = Firefox(service=service, options=options)
#         logger.info("WebDriver успешно запущен.")
#     except Exception as e:
#         logger.error(f"Ошибка при запуске WebDriver: {e}")
#         return

#     # Переходим на url юзера
#     logger.info(f"Переходим по URL: {original_url}")
#     driver.get(original_url)
#     sleep(2)

#     # Извлекаем полный url-адрес для дальнейшей работы
#     full_org_url = driver.current_url
#     logger.info(f"Полный URL компании: {full_org_url}")

#     org_url, reviews_url = process_url_yandex(full_org_url)

#     # Переходим на страницу компании и ждём полной загрузки
#     logger.info(f"Переходим на страницу компании: {org_url}")
#     driver.get(org_url)
#     sleep(5)

#     # Получаем название организации с обработкой ошибок
#     try:
#         org_name_element = driver.find_element(By.CSS_SELECTOR, ORG_NAME_BLOCK)
#         org_name = org_name_element.text.strip()
#     except NoSuchElementException:
#         org_name = None
#         logger.error("Не удалось найти название организации")

#     # Получаем полный адрес с обработкой ошибок
#     try:
#         address_element = driver.find_element(By.CLASS_NAME, ORG_ADDRESS_BLOCK)
#         full_address = address_element.text.strip()
#     except NoSuchElementException:
#         full_address = None
#         logger.error("Не удалось найти полный адрес")

#     # Проверяем, что данные получены перед сохранением в базу данных
#     if org_name is not None:
#         # Формирование общей информации о ресторане
#         restaurant_data = (org_name, org_url, full_address)
#         try:
#             create_restaurant(data=restaurant_data)
#             logger.info("Ресторан успешно добавлен в базу данных.")
#         except Exception as e:
#             logger.error(f"Ошибка при добавлении ресторана в базу данных: {e}")
#     else:
#         logger.info("Пропускаем ресторан, так как название не найдено.")

#     # Переходим на страницу с отзывами и ждём полной загрузки
#     logger.info(f"Переходим на страницу с отзывами: {reviews_url}")
#     driver.get(reviews_url)
#     sleep(5)

#     # Если сортировка успешно выбрана, продолжаем выполнение функции
#     # Вычисляем общее количество отзывов
#     try:
#         total_count_element = WebDriverWait(driver, 5).until(
#             EC.visibility_of_element_located(
#                 (By.CLASS_NAME, COUNT_REVIEWS_BLOCK)
#             )
#         )
#         total_count_text = total_count_element.text
#         total_count = int(total_count_text.split()[0])
#         logger.info(f"Общее количество отзывов: {total_count}")
#     except Exception as e:
#         logger.error(f"Ошибка при получении общего количества отзывов: {e}")
#         driver.quit()
#         return

#     sleep(2)

#     # Список для хранения всех уникальных отзывов
#     all_reviews = set()

#     # Функция для сбора отзывов с заданной сортировкой
#     def collect_reviews(sort_xpath):
#         logger.info(f"Сортировка по: {sort_xpath}")
#         attempt_count = 0
#         while attempt_count < 3:
#             try:
#                 # Ищем элемент сортировки и кликаем по нему
#                 filter_button = WebDriverWait(driver, 20).until(
#                     EC.element_to_be_clickable((By.CLASS_NAME, SORTED_BLOCK))
#                 )
#                 filter_button.click()

#                 # Ждем, пока появится элемент с нужной опцией и кликаем по нему
#                 sort_filter = WebDriverWait(driver, 20).until(
#                     EC.element_to_be_clickable((By.XPATH, sort_xpath))
#                 )
#                 # Прокручиваем до элемента (если нужно)
#                 driver.execute_script(
#                     "arguments[0].scrollIntoView();", sort_filter
#                 )

#                 # Кликаем по элементу сортировки
#                 sort_filter.click()
#                 logger.info(f"Сортировка {sort_xpath} выбрана.")
#                 sleep(5)
#                 break
#             except Exception as e:
#                 logger.error(f"Ошибка при выборе сортировки: {e}")
#                 attempt_count += 1
#                 if attempt_count == 3:
#                     logger.error("Ошибка на стороне сервера, попробуйте позже")
#                     driver.quit()
#                     return "Ошибка на стороне сервера, попробуйте позже"
#                 sleep(2)

#         # Прокручиваем страницу до конца, чтобы загрузить все отзывы
#         unique_reviews = set()
#         prev_reviews_count = 0
#         while (
#             len(unique_reviews) < total_count
#             and len(unique_reviews) < MAX_VIEW_REVIEWS
#         ):
#             logger.info(
#                 f'Уникальных отзывов в сортировке {sort_xpath}: '
#                 f'{len(unique_reviews)}'
#             )

#             # Получаем все отзывы на странице
#             reviews = driver.find_elements(By.CLASS_NAME, CARD_REVIEWS_BLOCK)

#             # Прокручиваем до последнего отзыва на странице
#             if reviews:
#                 # Проверяем, загрузились ли новые отзывы
#                 if scroll_to_bottom(driver, reviews[-1], prev_reviews_count):
#                     break  # Если новых отзывов нет, выходим
#                 prev_reviews_count = len(reviews)
#             # Сохраняем текущие отзывы из зоны видимости
#             for review in reviews:
#                 try:
#                     date_str = review.find_element(
#                         By.CSS_SELECTOR, DATE_ELEMENT
#                     ).get_attribute('content')
#                     review_date = datetime.strptime(
#                         date_str, "%Y-%m-%dT%H:%M:%S.%fZ"
#                     ).strftime(DATE_FORMAT)

#                     # Извлекаем имя автора
#                     author_name = review.find_element(
#                         By.CSS_SELECTOR,
#                         AUTHOR_ELEMENT
#                     ).text

#                     try:
#                         # Попытка найти значение рейтинга
#                         rating_value = WebDriverWait(review, 10).until(
#                             EC.presence_of_element_located(
#                                 (By.CSS_SELECTOR, RATING_ELEMENT)
#                             )
#                         ).get_attribute('content')
#                         rating_value = int(rating_value.split('.')[0])
#                     except Exception as e:
#                         logger.error(
#                             f"Ошибка при получении значения рейтинга: {e}"
#                         )
#                         rating_value = None

#                     # Текст отзыва
#                     text = review.find_element(
#                         By.CLASS_NAME, TEXT_ELEMENT
#                     ).text
#                     # Ищем ссылку на пользователя в текущем отзыве
#                     try:
#                         author_link = review.find_element(
#                             By.CSS_SELECTOR, LINK_ELEMENT
#                         ).get_attribute("href")
#                     except NoSuchElementException:
#                         logger.error("Не удалось найти ссылку на пользователя")
#                         author_link = None

#                     # Сохраняем данные отзыва
#                     review_entry = (
#                         review_date,
#                         author_name,
#                         author_link,
#                         rating_value,
#                         text,
#                     )
#                     unique_reviews.add(review_entry)

#                 except Exception as e:
#                     logger.error(f"Ошибка при получении информации: {e}")

#                     # Сохранение отзыва в множество для уникальности
#                     review_entry = (
#                         review_date,
#                         author_name,
#                         author_link,
#                         rating_value,
#                         text,
#                     )
#                     unique_reviews.add(review_entry)

#                 except Exception as e:
#                     logger.error(f"Ошибка при получении информации: {e}")

#             # Ждем небольшую паузу перед следующей прокруткой
#             sleep(7)

#         # Добавляем собранные уникальные отзывы в общий список
#         all_reviews.update(unique_reviews)

#     # Собираем отзывы по сортировке "По новизне"
#     collect_reviews(NEW_REVIEWS_SORTED)

#     # Изменяем сортировку, если общее количество отзывов больше 600
#     if total_count > MAX_VIEW_REVIEWS:
#         # Собираем отзывы по сортировке "Позитивные"
#         collect_reviews(POZITIVE_REVIEWS_SORTED)

#         # Собираем отзывы по сортировке "Негативные"
#         collect_reviews(NEGATIVE_REVIEWS_SORTED)

#         # Собираем отзывы по сортировке "По умолчанию"
#         collect_reviews(DEFAULT_REVIEWS_SORTED)

#     # Выводим количество собранных уникальных отзывов
#     logger.info(f"Общее количество уникальных отзывов: {len(all_reviews)}")

#     # Добавляем семантику и сортируем по дате
#     new_reviews_to_save = set()
#     for review in all_reviews:
#         # review_text = review[3]
#         semantic = None  # simple_semantic(review_text=review_text)
#         # добавляем семантическую оценку
#         review_with_semantic = review + (semantic,)
#         new_reviews_to_save.add(review_with_semantic)

#     # Сортировка отзывов по дате
#     sorted_reviews = sorted(
#         new_reviews_to_save,
#         key=lambda x: datetime.strptime(x[0], DATE_FORMAT)
#     )

#     # Определяем id ресторана для связи с отзывами
#     restaurant_data = read_some_restaurant_data(org_url=org_url)
#     restaurant_id = restaurant_data['id']
#     logger.info(f"ID ресторана: {restaurant_id}")

#     # Запись уникальных отзывов в базу данных
#     for review in sorted_reviews:
#         (
#             review_date, author_name, author_link, rating_value, text, semantic,
#         ) = review

#         review_data = (
#             restaurant_id,
#             review_date,
#             author_name,
#             author_link,
#             text,
#             semantic,
#             rating_value,
#         )
#         try:
#             create_review(review_data)
#         except Exception as e:
#             logger.error(f"Ошибка при добавлении отзыва в базу данных: {e}")

#     # Закрываем браузер
#     logger.info("Закрываем браузер.")
#     driver.quit()

#     return len(sorted_reviews)

def ya_prim_coll(original_url):
    logger.info(f"Начинаем сбор данных с URL: {original_url}")

    options = FirefoxOptions()
    options.add_argument('--headless')
    service = Service(DRIVER_PATH)

    try:
        logger.info("Запускаем Firefox WebDriver...")
        driver = Firefox(service=service, options=options)
        logger.info("WebDriver успешно запущен.")
    except Exception as e:
        logger.error(f"Ошибка при запуске WebDriver: {e}")
        return

    driver.get(original_url)
    sleep(2)
    full_org_url = driver.current_url
    logger.info(f"Полный URL компании: {full_org_url}")
    org_url, reviews_url = process_url_yandex(full_org_url)

    logger.info(f"Переходим на страницу компании: {org_url}")
    driver.get(org_url)
    sleep(5)

    try:
        org_name_element = driver.find_element(By.CSS_SELECTOR, ORG_NAME_BLOCK)
        org_name = org_name_element.text.strip()
    except NoSuchElementException:
        org_name = None
        logger.error("Не удалось найти название организации")

    try:
        address_element = driver.find_element(By.CLASS_NAME, ORG_ADDRESS_BLOCK)
        full_address = address_element.text.strip()
    except NoSuchElementException:
        full_address = None
        logger.error("Не удалось найти полный адрес")

    if org_name:
        restaurant_data = {'org_name': org_name, 'org_url': org_url, 'full_address': full_address}
        try:
            create_restaurant(data=restaurant_data)
            logger.info("Ресторан успешно добавлен в базу данных.")
        except Exception as e:
            logger.error(f"Ошибка при добавлении ресторана в базу данных: {e}")
    else:
        logger.info("Пропускаем ресторан, так как название не найдено.")

    logger.info(f"Переходим на страницу с отзывами: {reviews_url}")
    driver.get(reviews_url)
    sleep(5)

    try:
        total_count_element = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CLASS_NAME, COUNT_REVIEWS_BLOCK))
        )
        total_count_text = total_count_element.text
        total_count = int(total_count_text.split()[0])
        logger.info(f"Общее количество отзывов: {total_count}")
    except Exception as e:
        logger.error(f"Ошибка при получении общего количества отзывов: {e}")
        driver.quit()
        return

    sleep(2)
    all_reviews = set()

    def collect_reviews(sort_xpath):
        logger.info(f"Сортировка по: {sort_xpath}")
        attempt_count = 0
        while attempt_count < 3:
            try:
                filter_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, SORTED_BLOCK))
                )
                filter_button.click()

                sort_filter = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, sort_xpath))
                )
                driver.execute_script("arguments[0].scrollIntoView();", sort_filter)
                sort_filter.click()
                logger.info(f"Сортировка {sort_xpath} выбрана.")
                sleep(5)
                break
            except Exception as e:
                logger.error(f"Ошибка при выборе сортировки: {e}")
                attempt_count += 1
                if attempt_count == 3:
                    logger.error("Ошибка на стороне сервера, попробуйте позже")
                    driver.quit()
                    return "Ошибка на стороне сервера, попробуйте позже"
                sleep(2)

        unique_reviews = set()
        prev_reviews_count = 0
        while len(unique_reviews) < total_count and len(unique_reviews) < MAX_VIEW_REVIEWS:
            logger.info(f'Уникальных отзывов в сортировке {sort_xpath}: {len(unique_reviews)}')
            reviews = driver.find_elements(By.CLASS_NAME, CARD_REVIEWS_BLOCK)

            if reviews:
                if scroll_to_bottom(driver, reviews[-1], prev_reviews_count):
                    break
                prev_reviews_count = len(reviews)

            for review in reviews:
                try:
                    date_str = review.find_element(By.CSS_SELECTOR, DATE_ELEMENT).get_attribute('content')
                    review_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ").strftime(DATE_FORMAT)
                    author_name = review.find_element(By.CSS_SELECTOR, AUTHOR_ELEMENT).text

                    try:
                        rating_value = WebDriverWait(review, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, RATING_ELEMENT))
                        ).get_attribute('content')
                        rating_value = int(rating_value.split('.')[0])
                    except Exception as e:
                        rating_value = None

                    text = review.find_element(By.CLASS_NAME, TEXT_ELEMENT).text
                    author_link = None
                    try:
                        author_link = review.find_element(By.CSS_SELECTOR, LINK_ELEMENT).get_attribute("href")
                    except NoSuchElementException:
                        pass

                    review_entry = {
                        'review_date': review_date,
                        'author_name': author_name,
                        'author_link': author_link,
                        'rating_value': rating_value,
                        'text': text
                    }

                    unique_reviews.add(review_entry)

                except Exception as e:
                    logger.error(f"Ошибка при получении данных отзыва: {e}")

            sleep(7)

        all_reviews.update(unique_reviews)

    collect_reviews(NEW_REVIEWS_SORTED)

    if total_count > MAX_VIEW_REVIEWS:
        collect_reviews(POZITIVE_REVIEWS_SORTED)
        collect_reviews(NEGATIVE_REVIEWS_SORTED)
        collect_reviews(DEFAULT_REVIEWS_SORTED)

    logger.info(f"Общее количество уникальных отзывов: {len(all_reviews)}")

    new_reviews_to_save = set()
    for review in all_reviews:
        semantic = None
        review_with_semantic = review.copy()
        review_with_semantic['semantic'] = semantic
        new_reviews_to_save.add(review_with_semantic)

    sorted_reviews = sorted(
        new_reviews_to_save,
        key=lambda x: datetime.strptime(x['review_date'], DATE_FORMAT)
    )

    restaurant_data = read_some_restaurant_data(org_url=org_url)
    restaurant_id = restaurant_data['id']
    logger.info(f"ID ресторана: {restaurant_id}")

    for review in sorted_reviews:
        try:
            review_data = {
                'restaurant_id': restaurant_id,
                'review_date': review['review_date'],
                'author_name': review['author_name'],
                'author_link': review['author_link'],
                'text': review['text'],
                'semantic': review['semantic'],
                'rating_value': review['rating_value']
            }
            create_review(review_data)
        except Exception as e:
            logger.error(f"Ошибка при добавлении отзыва в базу данных: {e}")

    logger.info("Закрываем браузер.")
    driver.quit()

    return len(sorted_reviews)
