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
    # Получаем количесво отзывов за искомый месяц
    yandex_reviews = read_rest_ya_reviews_date(
        restaurant_id=restaurant_id,
        date_filter=previous_month
    ).count
    twogis_reviews = read_rest_twogis_reviews_date(
        restaurant_id=restaurant_id,
        date_filter=previous_month
    ).count
    total_count_reviews = yandex_reviews + twogis_reviews

    return total_count_reviews, twogis_reviews, yandex_reviews
