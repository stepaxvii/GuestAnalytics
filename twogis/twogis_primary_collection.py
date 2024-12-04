from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
from bs4 import BeautifulSoup
from time import sleep
from os import getenv
from dotenv import load_dotenv
import logging
from utils.date import formatted_date
from utils.twogis_validated_content import twogis_valid_content


load_dotenv()
logging.basicConfig(level=logging.INFO)

logging.info("Скрипт запущен.")


DRIVER_PATH = getenv('DRIVER_PATH', default='')
validated_url = 'https://2gis.ru/sochi/firm/70000001067211531/tab/reviews'


def twogis_prim_coll(url):
    options = FirefoxOptions()
    #options.add_argument('--headless')
    service = Service(DRIVER_PATH)
    driver = Firefox(service=service, options=options)
    actions = ActionChains(driver)

    # Определяем текущую дату
    actual_date = datetime.now().strftime("%Y-%m-%d")
    print(actual_date)

    # Переходим на страницу с отзывами и ждём полной загрузки
    driver.get(url)
    sleep(5)

    # Извлекаем актуальные названия блоков
    (review_block, author_class, review_text_class,
     rating_class, date_class) = twogis_valid_content(url)
    logging.INFO(review_block, author_class,
                 review_text_class, rating_class, date_class)

    if url.startswith('https://2gis.ru/'):
        total_reviews_element = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//a[contains(@class, "_rdxuhv3")]/span'))
        )
        total_reviews_text = total_reviews_element.text
        total_count = int(total_reviews_text)
        print(f"Общее количество отзывов: {total_count}")

        with open("test_2g_docs.txt", "w", encoding='utf-8') as file:
            attempts = 0
            unique_reviews = set()

            while attempts < 5 and len(unique_reviews) < total_count:
                reviews_block = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, review_block))
                )
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                reviews = soup.find_all('div', class_='_1k5soqfl')

                for review in reviews:
                    try:
                        date_str = review.find(
                            'div', class_=date_class).get_text(strip=True)
                        date_str = date_str.split(',')[0].strip()
                        formatted_review_date = formatted_date(
                            date_str=date_str)

                        author = review.find('span', class_=author_class)
                        author_name = author.get_text(
                            strip=True) if author else "Автор не найден"

                        rating_stars = review.find_all('svg', fill="#ffb81c")
                        rating = len(rating_stars)

                        review_text = review.find(
                            'a', class_=review_text_class)
                        review_text_content = review_text.get_text(
                            strip=True) if review_text else "Текст не найден"

                        # Проверка наличия текста отзыва
                        if review_text_content == "Текст отзыва не найден":
                            print(f"Отзыв без текста: {date_str}, Автор: {author_name}, Рейтинг: {rating}.0")

                            # Вернёмся к блоку с отзывами и ищем текст по имени
                            # Получаем все отзывы снова
                            all_reviews = driver.find_elements(
                                By.CLASS_NAME, review_block)
                            for r in all_reviews:
                                try:
                                    author_check = r.find(
                                        'span', class_=author_class)
                                    if author_check and author_check.get_text(strip=True) == author_name:
                                        # Если нашли отзыв с таким же автором
                                        new_review_text = r.find(
                                            'a', class_=review_text_class)
                                        if new_review_text:
                                            review_text_content = new_review_text.get_text(strip=True)
                                            print(f"Текст отзыва найден при повторной проверке: {review_text_content}")
                                            break  # Выходим из цикла после нахождения текста
                                except Exception as e:
                                    print(f"Ошибка при повторной проверке текста отзыва: {e}")

                        # Создаем запись отзыва
                        review_entry = (
                            formatted_review_date,
                            '2gis',
                            author_name,
                            f'{rating}.0',
                            review_text_content,
                        )

                        unique_reviews.add(review_entry)
                        print(f'Количество уникальных отзывов: {len(unique_reviews)}')

                    except Exception as e:
                        print(f"Ошибка при получении информации об отзыве: {e}")

                # Прокрутка страницы вниз на фиксированное расстояние (например, 100 пикселей)
                previous_height = driver.execute_script("return arguments[0].scrollHeight", reviews_block)
                driver.execute_script("arguments[0].scrollTop += 100;", reviews_block)
                sleep(3)  # Увеличьте время ожидания

                new_height = driver.execute_script("return arguments[0].scrollHeight", reviews_block)

                if new_height == previous_height:
                    attempts += 1  # Увеличиваем счетчик неудачных попыток
                    print("Не удалось загрузить новые отзывы.")
                else:
                    attempts = 0  # Сбрасываем счетчик неудачных попыток

            sorted_reviews = sorted(unique_reviews, key=lambda x: datetime.strptime(x[0], '%Y-%m-%d'), reverse=True)

            for review in sorted_reviews:
                file.write(f"{review}\n")

    print("Сбор данных завершен.")

    # Закрываем браузер
    driver.quit()
    return 'DONE!'


print(twogis_prim_coll(url=validated_url))
