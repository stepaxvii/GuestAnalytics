from datetime import datetime, timedelta

from constants import DATE_FORMAT, DATE_FORMAT_FOR_MONTH_INSIGHT


def handle_date(date_str, actual_date):
    # Убираем суффикс ", отредактирован", если он есть
    if ', отредактирован' in date_str:
        date_str = date_str.replace(', отредактирован', '')
    # Обработка слова "сегодня"
    if "сегодня" in date_str.lower():
        return actual_date
    # Обработка слова "вчера"
    elif "вчера" in date_str.lower():
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        return yesterday
    else:
        # Если дата в другом формате, используем существующую логику
        try:
            return formatted_date(date_str)
        except ValueError:
            print(f"Не удалось обработать дату: {date_str}")
            return actual_date  # Если ошибка, возвращаем текущую дату


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


def check_month(date: str):
    """Функция проверки необходимого месяца и даты для инсайтов."""

    current_date = datetime.now()

    if current_date.month == 1:
        last_month = current_date.replace(
            year=current_date.year - 1, month=12
        )
    else:
        last_month = current_date.replace(
            month=current_date.month - 1
        )

    # Приводим к формату строки "гггг-мм"
    last_month = last_month.strftime('%Y-%m')

    # Возвращаем True, если значения совпадают.
    return date == last_month, last_month


def make_last_months(current_date: datetime):
    """Функция выявления предыдущего и позапрошлого месяцев."""

    if current_date.month == 1:
        last_month = current_date.replace(year=current_date.year - 1, month=12)
        month_bef_last = last_month.replace(month=11)
    elif current_date.month == 2:
        last_month = current_date.replace(month=1)
        month_bef_last = current_date.replace(
            year=current_date.year - 1, month=12
        )
    else:
        last_month = current_date.replace(month=current_date.month - 1)
        month_bef_last = current_date.replace(month=current_date.month - 2)

    last_month = last_month.strftime(DATE_FORMAT_FOR_MONTH_INSIGHT)
    month_bef_last = month_bef_last.strftime(DATE_FORMAT_FOR_MONTH_INSIGHT)

    return last_month, month_bef_last


def month_for_prim_coll():
    """Функция выявления двух последних месяцев для первичных инсайтов."""

    # Выявляем текущую дату
    current_date = datetime.now()
    last_month, month_bef_last = make_last_months(current_date=current_date)

    return last_month, month_bef_last
