from api.db import session
from data.data_main import (
    TwogisReview,
    Restaurant,
    RestaurantInsight,
    YandexReview
)


def read_all_restaurant_data():
    """Получаем информацию обо всех ресторанах из БД."""

    restaurants = session.query(Restaurant).all()

    # Преобразование объектов в список словарей
    restaurants_list = [
        {
            "id": restaurant.id,
            "wp_id": restaurant.wp_id,
            "title": restaurant.title,
            "yandex_link": restaurant.yandex_link,
            "twogis_link": restaurant.twogis_link,
            "address": restaurant.address,
            "tg_channal": restaurant.tg_channal,
            "subscription": restaurant.subscription,
        }
        for restaurant in restaurants
    ]

    return restaurants_list


def read_restaurant_data(rest_data):
    """
    Получаем информацию о ресторане по id или ссылке.

    :param rest_data: id (int) или ссылка (str) на ресторан.
    :return: Словарь с данными ресторана или None, если ресторан не найден.
    :raises ValueError: Если передан неподходящий тип данных.
    """
    if not isinstance(rest_data, (int, str)):
        raise ValueError("Данные должны быть (int) или (str).")

    if isinstance(rest_data, int):
        # Если передано число, ищем по id
        restaurant = session.query(Restaurant).filter(
            Restaurant.id == rest_data
        ).first()
    else:
        # Иначе ищем по ссылкам
        if 'yandex' in rest_data:  # Если в строке есть ссылка на Yandex
            restaurant = session.query(Restaurant).filter(
                Restaurant.yandex_link == rest_data
            ).first()
        else:
            restaurant = session.query(Restaurant).filter(
                Restaurant.twogis_link == rest_data
            ).first()

    if restaurant:
        return {
            "id": restaurant.id,
            "wp_id": restaurant.wp_id,
            "title": restaurant.title,
            "yandex_link": restaurant.yandex_link,
            "twogis_link": restaurant.twogis_link,
            "address": restaurant.address,
            "tg_channal": restaurant.tg_channal,
            "subscription": restaurant.subscription
        }
    else:
        return None


def read_restaurant_by_wp(wp_id):
    """Получения данных ресторана по wp_id."""

    restaurant = session.query(Restaurant).filter(
        Restaurant.wp_id == wp_id
    ).first()

    if restaurant:
        return {
            "id": restaurant.id,
            "wp_id": restaurant.wp_id,
            "title": restaurant.title,
            "yandex_link": restaurant.yandex_link,
            "twogis_link": restaurant.twogis_link,
            "address": restaurant.address,
            "tg_channal": restaurant.tg_channal,
            "subscription": restaurant.subscription
        }
    else:
        return None


def read_rest_ya_reviews(restaurant_id):
    """Получаем отзывы с Яндекса определённого ресторана."""

    return session.query(YandexReview).filter(
        YandexReview.restaurant_id == restaurant_id
    ).all()


def read_rest_ya_reviews_date(restaurant_id, date_filter):
    """Получаем отзывы с Яндекса определённого ресторана, фильтруя по дате."""
    return session.query(YandexReview).filter(
        YandexReview.restaurant_id == restaurant_id,
        YandexReview.created_at.startswith(date_filter)
    ).all()


def read_rest_twogis_reviews(restaurant_id):
    """Получаем отзывы с 2GIS определённого ресторана."""

    return session.query(TwogisReview).filter(
        TwogisReview.restaurant_id == restaurant_id
    ).all()


def read_rest_twogis_reviews_date(restaurant_id, date_filter):
    """Получаем отзывы с 2GIS определённого ресторана, фильтруя по дате."""
    return session.query(TwogisReview).filter(
        TwogisReview.restaurant_id == restaurant_id,
        TwogisReview.created_at.startswith(date_filter)
    ).all()


def read_rest_month_insight(restaurant_id: int, month: str):
    """Получаем инсайт ресторана за указанный месяц (формат 'YYYY-MM')."""
    insight = session.query(RestaurantInsight).filter(
        RestaurantInsight.restaurant_id == restaurant_id,
        RestaurantInsight.period == month
    ).first()

    return insight


def read_rest_month_insight_list(restaurant_id):
    """Получаем инсайты списком за прошедший месяц."""
    insight = session.query(RestaurantInsight).filter(
        RestaurantInsight.restaurant_id == restaurant_id
    ).order_by(RestaurantInsight.id.desc()).first()

    # Если инсайт найден
    if insight and insight.insight:
        # Разбиваем текст инсайта по точке и убираем лишние пробелы
        insights = [
            insight_part.strip() for insight_part
            in insight.insight.split('.') if insight_part.strip()
        ]
        return insights

    # Если инсайт не найден
    return ['Анализ не завершён.']
