from sqlalchemy.exc import IntegrityError

from constants import TG_CHANNAL
from data_base.data_main import session, Restaurant, YandexReview


def create_restaurant(data):
    """Создание ресторана."""

    # Извлекаем данные из собранной о ресторане информации
    title, yandex_link, address = data

    try:
        restaurant = Restaurant(
            title=title,
            yandex_link=yandex_link,
            address=address,
            tg_channal=TG_CHANNAL
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
    restaurant_id, created_at, author, rating, content, semantic = data

    review = YandexReview(
        restaurant_id=restaurant_id,
        created_at=created_at,
        author=author,
        rating=rating,
        content=content,
        semantic=semantic
    )
    session.add(review)
    session.commit()
    session.close
