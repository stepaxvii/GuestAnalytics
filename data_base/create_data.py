import logging

from os import getenv

from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from data_base.data_main import session, Restaurant, YandexReview

load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TG_GROUP = getenv('TG_GROUP')


def create_restaurant(data):
    """Создание ресторана."""

    # Извлекаем данные из собранной о ресторане информации
    id, title, yandex_link, address = data

    try:
        restaurant = Restaurant(
            id=id,
            title=title,
            yandex_link=yandex_link,
            address=address,
            tg_channal=TG_GROUP
        )
        session.add(restaurant)
        session.commit()
    except IntegrityError as e:
        session.rollback()
        print(f'Ошибка уникальности: {e}')
    session.close()


def create_review(data):
    """Создание отзыва из словаря."""

    # Извлекаем данные из словаря
    restaurant_id = data.get('restaurant_id')
    created_at = data.get('review_date')
    author = data.get('author_name')
    link = data.get('author_link', None)
    rating = data.get('rating_value')
    content = data.get('text')
    semantic = data.get('semantic', None)

    # Проверка значений
    if not created_at:
        raise ValueError("Поле 'review_date' обязательно.")
    if not author:
        raise ValueError("Поле 'author_name' обязательно.")
    if rating is None:
        rating = 0

    # Создаем экземпляр YandexReview с данными из словаря
    review = YandexReview(
        restaurant_id=restaurant_id,
        created_at=created_at,
        author=author,
        link=link,
        rating=rating,
        content=content,
        semantic=semantic,
    )

    try:
        # Добавляем и коммитим запись в базу данных
        session.add(review)
        session.commit()
    except Exception as e:
        session.rollback()  # Откат транзакции при ошибке
        logger.error(f"Ошибка при добавлении отзыва в базу данных: {e}")
    finally:
        session.close()
