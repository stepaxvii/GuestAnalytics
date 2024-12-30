from data_base.data_main import session, Restaurant


def read_restaurant_data(org_url):
    """Получаем информацию о ресторане, учитывая ссылку на сервис."""

    restaurant = session.query(Restaurant).filter(
        Restaurant.yandex_link == org_url
    ).first()
    id = restaurant.id
    company_id = restaurant.company_id
    title = restaurant.title
    yandex_link = restaurant.yandex_link
    twogis_link = restaurant.twogis_link
    address = restaurant.address
    subs = restaurant.subs
    manager_name = restaurant.manager_name
    manager_contact = restaurant.manager_contact
    email = restaurant.email

    return (
        id,
        company_id,
        title,
        yandex_link,
        twogis_link,
        address,
        subs,
        manager_name,
        manager_contact,
        email
    )
