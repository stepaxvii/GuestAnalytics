from api.db import session
from data.data_main import Restaurant, YandexReview


def read_all_restaurant_data():
    """Получаем информацию обо всех ресторанах из БД."""

    restaurants = session.query(Restaurant).all()

    # Преобразование объектов в список словарей
    restaurants_list = [
        {
            "id": restaurant.id,
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


def read_restaurant_data(identifier):
    """
    Получаем информацию о ресторане по id или ссылке.

    :param identifier: id (int) или ссылка (str) на ресторан.
    :return: Словарь с данными ресторана или None, если ресторан не найден.
    :raises ValueError: Если передан неподходящий тип данных.
    """
    if not isinstance(identifier, (int, str)):
        raise ValueError("Идентификатор должен быть (int) или (str).")

    if isinstance(identifier, int):
        # Если передано число, ищем по id
        restaurant = session.query(Restaurant).filter(
            Restaurant.id == identifier
        ).first()
    else:
        # Иначе ищем по yandex_link
        restaurant = session.query(Restaurant).filter(
            Restaurant.yandex_link == identifier
        ).first()

    if restaurant:
        return {
            "id": restaurant.id,
            "title": restaurant.title,
            "yandex_link": restaurant.yandex_link,
            "twogis_link": restaurant.twogis_link,
            "address": restaurant.address,
            "tg_channal": restaurant.tg_channal,
            "subscription": restaurant.subscription
        }
    else:
        return None  # Если ресторан не найден


def read_rest_ya_reviews(restaurant_id):
    """Получаем отзывы с Яндекса определённого ресторана."""

    return session.query(YandexReview).filter(
        YandexReview.restaurant_id == restaurant_id
    ).all()
