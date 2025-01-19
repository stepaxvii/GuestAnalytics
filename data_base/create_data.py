from os import getenv

from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from data_base.data_main import session, Restaurant, YandexReview

load_dotenv()

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
    """Создание отзыва."""

    # Извлекаем данные из уникального отзыва и приводим в необходимый формат
    restaurant_id, created_at, author, link, content, semantic, rating = data

    review = YandexReview(
        restaurant_id=restaurant_id,
        created_at=created_at,
        author=author,
        rating=rating,
        content=content,
        semantic=semantic,
        link=link,
    )
    session.add(review)
    session.commit()
    session.close
