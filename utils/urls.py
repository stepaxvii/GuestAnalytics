def process_url_yandex(original_url):
    """Функция форматирования валидного адреса для Яндекса."""

    org_url = original_url.split('?')[0]
    reviews_url = org_url + 'reviews'

    return org_url, reviews_url


def process_url_twogis(original_url):
    """Функция форматирования валидного адреса для 2ГИС."""

    question_mark_index = original_url.find("?")

    if question_mark_index != -1:
        return original_url[:question_mark_index] + "/tab/reviews"

    return original_url + "/tab/reviews"
