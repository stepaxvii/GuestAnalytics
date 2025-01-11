from data_base.data_main import session, Restaurant, YandexReview


def read_all_restaurant_data():
    """Получаем информацию обо всех ресторанах из БД."""

    restaurants = session.query(Restaurant).all()

    # Преобразование объектов в список словарей
    restaurants_list = [
        {
            "id": restaurant.id,
            "company_id": restaurant.company_id,
            "title": restaurant.title,
            "yandex_link": restaurant.yandex_link,
            "twogis_link": restaurant.twogis_link,
            "address": restaurant.address,
            "subs": restaurant.subs,
            "manager_name": restaurant.manager_name,
            "manager_contact": restaurant.manager_contact,
            "tg_channal": restaurant.tg_channal,
            "email": restaurant.email
        }
        for restaurant in restaurants
    ]

    return restaurants_list


def read_some_restaurant_data(org_url):
    """Получаем информацию о ресторане, учитывая ссылку на сервис."""

    restaurant = session.query(Restaurant).filter(
        Restaurant.yandex_link == org_url
    ).first()

    return {
        "id": restaurant.id,
        "company_id": restaurant.company_id,
        "title": restaurant.title,
        "yandex_link": restaurant.yandex_link,
        "twogis_link": restaurant.twogis_link,
        "address": restaurant.address,
        "subs": restaurant.subs,
        "manager_name": restaurant.manager_name,
        "manager_contact": restaurant.manager_contact,
        "email": restaurant.email,
        "tg_channal": restaurant.tg_channal
    }


def read_rest_ya_reviews(restaurant_id):
    """Получаем отзывы с Яндекса определённого ресторана."""

    return session.query(YandexReview).filter(
        YandexReview.restaurant_id == restaurant_id
    ).all()
