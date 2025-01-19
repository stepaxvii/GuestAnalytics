import logging

from os import getenv

from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from data_base.data_main import session, Restaurant, YandexReview

load_dotenv()

# Настройка логирования (можно настроить формат и уровень логирования)
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)

TG_GROUP = getenv('TG_GROUP')


def create_restaurant(data):
    """Создание ресторана."""

    # Извлекаем данные из собранной о ресторане информации
    title, yandex_link, address = data

    try:
        restaurant = Restaurant(
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
    link = data.get('author_link', None)  # Используем .get(), чтобы избежать KeyError, если ключ отсутствует
    content = data.get('text')
    semantic = data.get('semantic', None)  # Используем .get(), чтобы проверить наличие semantic
    rating = data.get('rating_value')

    # Создаем экземпляр YandexReview с данными из словаря
    review = YandexReview(
        restaurant_id=restaurant_id,
        created_at=created_at,
        author=author,
        rating=rating,
        content=content,
        semantic=semantic,
        link=link,
    )
    
    try:
        # Добавляем и коммитим запись в базу данных
        session.add(review)
        session.commit()

        # Логируем информацию о сохранённом отзыве
        logging.info(
            f"Отзыв сохранён: Дата - {created_at}, "
            f"Автор - {author}, Рейтинг - {rating}"
        )

    except Exception as e:
        # Логируем ошибку, если что-то пошло не так
        logging.error(f"Ошибка при сохранении отзыва: {e}")
    finally:
        # Закрываем сессию, чтобы избежать утечек ресурсов
        session.close()

