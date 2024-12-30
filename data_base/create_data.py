from data_base.data_main import session, Restaurant, YandexReview
from datetime import datetime


def create_restaurant(data):
    """Создание ресторана."""

    # Извлекаем данные из собранной о ресторане информации
    title, yandex_link, address = data

    restaurant = Restaurant(
        title=title,
        yandex_link=yandex_link,
        address=address
    )
    session.add(restaurant)
    session.commit()
    session.close()


def create_review(data):
    """Создание отзыва."""

    # Извлекаем данные из уникального отзыва и приводим в необходимый формат
    restaurant_id, created_at_str, author, rating_str, content = data
    created_at = datetime.strptime(created_at_str, '%Y-%m-%d').date()
    rating = int(rating_str.split('.')[0])

    review = YandexReview(
        restaurant_id=restaurant_id,
        created_at=created_at,
        author=author,
        rating=rating,
        content=content
    )
    session.add(review)
    session.commit()
    session.close
