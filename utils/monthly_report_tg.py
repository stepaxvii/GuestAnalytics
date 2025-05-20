from collections import Counter
from datetime import datetime

from data.read_data import (
    read_rest_twogis_reviews_date,
    read_rest_ya_reviews_date
)
from utils.date import make_last_months


def get_previous_month():
    """Функция для определения предыдущего месяца."""

    # определяем текущую дату
    current_date = datetime.now()
    # Получаем предыдущий месяц
    previous_month = make_last_months(
        current_date=current_date
    )[0]

    return previous_month


def get_count_reviews(restaurant_id: int):
    """Функция определения количества отзывов за месяц."""

    previous_month = get_previous_month()
    # Получаем количество отзывов за искомый месяц
    yandex_reviews = len(read_rest_ya_reviews_date(
        restaurant_id=restaurant_id,
        date_filter=previous_month
    ))
    twogis_reviews = len(read_rest_twogis_reviews_date(
        restaurant_id=restaurant_id,
        date_filter=previous_month
    ))
    total_count_reviews = yandex_reviews + twogis_reviews

    return total_count_reviews, twogis_reviews, yandex_reviews


def avg_rest_rating(restaurant_id):
    """Получаем средний рейтинг отзывов с Яндекса и TwoGIS за прошлый месяц."""

    # Получаем предыдущий месяц
    previous_month = get_previous_month()

    # Получаем отзывы с Яндекса за предыдущий месяц
    yandex_reviews = read_rest_ya_reviews_date(
        restaurant_id=restaurant_id,
        date_filter=previous_month
    )

    # Получаем отзывы с TwoGIS за предыдущий месяц
    twogis_reviews = read_rest_twogis_reviews_date(
        restaurant_id=restaurant_id,
        date_filter=previous_month
    )

    # Если отзывы есть, рассчитываем средний рейтинг, иначе возвращаем 0
    if yandex_reviews:
        yandex_avg_rating = sum(
            [review.rating for review in yandex_reviews]
        ) / len(yandex_reviews)
    else:
        yandex_avg_rating = None

    if twogis_reviews:
        twogis_avg_rating = sum(
            [review.rating for review in twogis_reviews]
        ) / len(twogis_reviews)
    else:
        twogis_avg_rating = None

    # Если на одной из платформ есть отзывы, считаем рейтинг только по ней
    if yandex_avg_rating is not None and twogis_avg_rating is not None:
        average_rating = round((yandex_avg_rating + twogis_avg_rating) / 2, 1)
    elif yandex_avg_rating is not None:
        average_rating = round(yandex_avg_rating, 1)
    elif twogis_avg_rating is not None:
        average_rating = round(twogis_avg_rating, 1)
    else:
        average_rating = 0

    return (
        round(average_rating, 1),
        round((twogis_avg_rating if twogis_avg_rating is not None else 0), 1),
        round((yandex_avg_rating if yandex_avg_rating is not None else 0), 1)
    )


def count_reviews_by_rating(restaurant_id: int):
    """Подсчитываем количество отзывов с разным рейтингом."""
    # Получаем предыдущий месяц
    previous_month = get_previous_month()

    # Получаем отзывы с Яндекса за предыдущий месяц
    yandex_reviews = read_rest_ya_reviews_date(
        restaurant_id=restaurant_id,
        date_filter=previous_month
    )

    # Получаем отзывы с TwoGIS за предыдущий месяц
    twogis_reviews = read_rest_twogis_reviews_date(
        restaurant_id=restaurant_id,
        date_filter=previous_month
    )

    # Подсчитываем количество отзывов с каждым рейтингом на Яндексе
    if yandex_reviews:
        yandex_ratings = [review.rating for review in yandex_reviews]
        yandex_rating_count = dict(Counter(yandex_ratings))
    else:
        yandex_rating_count = {}

    # Подсчитываем количество отзывов с каждым рейтингом на TwoGIS
    if twogis_reviews:
        twogis_ratings = [review.rating for review in twogis_reviews]
        twogis_rating_count = dict(Counter(twogis_ratings))
    else:
        twogis_rating_count = {}

    # Сливаем результаты с двух платформ
    combined_rating_count = yandex_rating_count.copy()
    for rating, count in twogis_rating_count.items():
        combined_rating_count[
            rating
        ] = combined_rating_count.get(rating, 0) + count

    return combined_rating_count
