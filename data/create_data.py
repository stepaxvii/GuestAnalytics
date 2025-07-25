import logging

from os import getenv

from sqlalchemy.exc import IntegrityError, PendingRollbackError
from dotenv import load_dotenv

from api.db import session
from data.data_main import (
    Restaurant,
    RestaurantInsight,
    TwogisReview,
    YandexReview
)

load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TG_GROUP = getenv('TG_GROUP')


def create_restaurant(data):
    """Создание ресторана."""

    # Извлекаем данные из собранной о ресторане информации
    title, yandex_link, address, tg_channal = data

    try:
        restaurant = Restaurant(
            title=title,
            yandex_link=yandex_link,
            address=address,
            tg_channal=tg_channal,
        )
        session.add(restaurant)
        session.commit()
    except IntegrityError as e:
        session.rollback()
        print(f'Ошибка уникальности: {e}')
    session.close()


def create_ya_review(data):
    """Создание Яндекс отзыва из словаря."""

    # Извлекаем данные из словаря
    restaurant_id = data.get('restaurant_id')
    created_at = data.get('review_date')
    author = data.get('author_name', 'Аноним')
    link = data.get('author_link', None)
    rating = data.get('rating_value', 0)
    content = data.get('text')
    semantic = data.get('semantic', None)

    # Проверка обязательных полей
    if not created_at:
        raise ValueError("Поле 'review_date' обязательно.")
    if not content:
        raise ValueError("Поле 'text' обязательно.")

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
    except PendingRollbackError as e:
        # Специальная обработка ошибки при наличии неоконченной транзакции
        session.rollback()
        logger.error(f"Ошибка с транзакцией: {e}")
    except Exception as e:
        session.rollback()  # Откат транзакции при ошибке
        logger.error(f"Ошибка при добавлении отзыва в базу данных: {e}")
    finally:
        session.close()


def create_twogis_review(data):
    """Создание 2GIS отзыва из словаря."""

    # Извлекаем данные из словаря
    restaurant_id = data.get('restaurant_id')
    created_at = data.get('review_date')
    author = data.get('author_name', 'Аноним')
    link = data.get('author_link', None)
    rating = data.get('rating_value', 0)
    content = data.get('text')
    semantic = data.get('semantic', None)

    # Проверка обязательных полей
    if not created_at:
        raise ValueError("Поле 'review_date' обязательно.")
    if not content:
        raise ValueError("Поле 'text' обязательно.")

    # Создаем экземпляр 2GIS с данными из словаря
    review = TwogisReview(
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
    except PendingRollbackError as e:
        # Специальная обработка ошибки при наличии неоконченной транзакции
        session.rollback()
        logger.error(f"Ошибка с транзакцией: {e}")
    except Exception as e:
        session.rollback()  # Откат транзакции при ошибке
        logger.error(f"Ошибка при добавлении отзыва в базу данных: {e}")
    finally:
        session.close()


def create_insight(data):
    """Создание ежемесячного инсайта."""

    restaurant_id, period, insight = data

    month_insight = RestaurantInsight(
        restaurant_id=restaurant_id,
        period=period,
        insight=insight
    )

    try:
        # Добавляем и коммитим запись в базу данных
        session.add(month_insight)
        session.commit()
    except PendingRollbackError as e:
        # Специальная обработка ошибки при наличии неоконченной транзакции
        session.rollback()
        logger.error(f"Ошибка с транзакцией: {e}")
    except Exception as e:
        session.rollback()  # Откат транзакции при ошибке
        logger.error(f"Ошибка при добавлении отзыва в базу данных: {e}")
    finally:
        session.close()
