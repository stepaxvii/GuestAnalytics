from datetime import datetime

from constants import DATE_FORMAT


def formatted_date(date_str):
    month_mapping = {
        "января": "01",
        "февраля": "02",
        "марта": "03",
        "апреля": "04",
        "мая": "05",
        "июня": "06",
        "июля": "07",
        "августа": "08",
        "сентября": "09",
        "октября": "10",
        "ноября": "11",
        "декабря": "12"
    }

    for month_name, month_number in month_mapping.items():
        if month_name in date_str:
            date_str = date_str.replace(month_name, month_number)

    review_date = datetime.strptime(date_str, '%d %m %Y')
    formatted_review_date = review_date.strftime(DATE_FORMAT)

    return formatted_review_date


month_dict = {
    "01": "январь",
    "02": "февраль",
    "03": "март",
    "04": "апрель",
    "05": "май",
    "06": "июнь",
    "07": "июль",
    "08": "август",
    "09": "сентябрь",
    "10": "октябрь",
    "11": "ноябрь",
    "12": "декабрь"
}
