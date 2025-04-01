from datetime import datetime
from sqlalchemy import func
from sqlalchemy.types import Date as DATE
from api.db import session
from data.data_main import YandexReview, TwogisReview

# Словарь для нужного формата дат в dashboard
month_dict = {
    "01": "янв",
    "02": "фев",
    "03": "мар",
    "04": "апр",
    "05": "май",
    "06": "июн",
    "07": "июл",
    "08": "авг",
    "09": "сен",
    "10": "окт",
    "11": "ноя",
    "12": "дек"
}


def count_rest_ya_reviews(restaurant_id):
    """Получаем количество отзывов с Яндекса определённого ресторана."""
    try:
        return session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id
        ).count()
    except Exception as e:
        session.rollback()
        raise e


def count_rest_twogis_reviews(restaurant_id):
    """Получаем количество отзывов с Яндекса определённого ресторана."""
    try:
        return session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id
        ).count()
    except Exception as e:
        session.rollback()
        raise e


def count_reviews_last_year(restaurant_id):
    """
    Получаем количество отзывов за последний год
    с Яндекса для определённого ресторана.
    """
    try:
        # Текущая дата
        current_date = datetime.now()

        # Дата год назад (месяц назад)
        start_date = current_date.replace(year=current_date.year - 1, day=1)

        # Преобразуем обе даты в формат "YYYY-MM"
        current_month_str = current_date.strftime("%Y-%m")
        start_month_str = start_date.strftime("%Y-%m")

        # Подсчитываем отзывы с Яндекса в последний год (по месяцам)
        ya_total_reviews = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            func.substr(YandexReview.created_at, 1, 7) >= start_month_str,
            func.substr(YandexReview.created_at, 1, 7) <= current_month_str
        ).count()

        # Подсчитываем отзывы с 2ГИС в последний год (по месяцам)
        twogis_total_reviews = session.query(TwogisReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            func.substr(TwogisReview.created_at, 1, 7) >= start_month_str,
            func.substr(TwogisReview.created_at, 1, 7) <= current_month_str
        ).count()

        # Общее количество отзывов
        total_reviews = ya_total_reviews + twogis_total_reviews

        return total_reviews
    except Exception as e:
        session.rollback()
        raise e


# def avg_rest_rating(restaurant_id):
#     """Получаем среднее значение рейтинга отзывов с Яндекса для ресторана."""
#     try:
#         return round(session.query(func.avg(YandexReview.rating)).filter(
#             YandexReview.restaurant_id == restaurant_id
#         ).scalar(), 1)
#     except Exception as e:
#         session.rollback()
#         raise e

def avg_rest_rating(restaurant_id):
    """Получаем среднее значение рейтинга отзывов с Яндекса и 2ГИС для ресторана."""
    try:
        # Вычисляем среднее значение для обеих площадок
        avg_ya_rating = session.query(func.avg(YandexReview.rating)).filter(
            YandexReview.restaurant_id == restaurant_id
        ).scalar() or 0  # если нет данных, то считаем как 0

        avg_twogis_rating = session.query(func.avg(TwogisReview.rating)).filter(
            TwogisReview.restaurant_id == restaurant_id
        ).scalar() or 0  # если нет данных, то считаем как 0

        # Считаем среднее между двумя площадками
        total_reviews = session.query(func.count(YandexReview.id)).filter(
            YandexReview.restaurant_id == restaurant_id
        ).scalar() or 0  # Считаем количество отзывов на Яндексе

        total_reviews_twogis = session.query(func.count(TwogisReview.id)).filter(
            TwogisReview.restaurant_id == restaurant_id
        ).scalar() or 0  # Считаем количество отзывов на 2ГИС

        total_reviews_count = total_reviews + total_reviews_twogis
        if total_reviews_count > 0:
            weighted_avg_rating = ((avg_ya_rating * total_reviews) + (avg_twogis_rating * total_reviews_twogis)) / total_reviews_count
        else:
            weighted_avg_rating = 0  # если нет отзывов, то считаем рейтинг как 0

        return round(weighted_avg_rating, 1)

    except Exception as e:
        session.rollback()
        raise e


# def calculate_nps(restaurant_id):
#     """Рассчитываем NPS для ресторана."""
#     try:
#         total_reviews = session.query(YandexReview).filter(
#             YandexReview.restaurant_id == restaurant_id
#         ).count()

#         if total_reviews == 0:
#             return 0

#         # Количество Promoters (5 звезд)
#         promoters_count = session.query(YandexReview).filter(
#             YandexReview.restaurant_id == restaurant_id,
#             YandexReview.rating == 5
#         ).count()

#         # Количество Detractors (1, 2, или 3 звезды)
#         detractors_count = session.query(YandexReview).filter(
#             YandexReview.restaurant_id == restaurant_id,
#             YandexReview.rating.in_([1, 2, 3])
#         ).count()

#         # Рассчитываем проценты
#         promoters_percent = (promoters_count / total_reviews) * 100
#         detractors_percent = (detractors_count / total_reviews) * 100

#         # NPS = Promoters - Detractors
#         nps = round(promoters_percent - detractors_percent, 1)
#         return nps
#     except Exception as e:
#         session.rollback()
#         raise e


# def calculate_nps_for_month(restaurant_id, year, month):
#     """Рассчитываем NPS для ресторана за конкретный месяц."""
#     try:
#         start_date = datetime(year, month, 1)
#         end_date = datetime(
#             year, month + 1, 1
#         ) if month < 12 else datetime(year + 1, 1, 1)

#         total_reviews = session.query(YandexReview).filter(
#             YandexReview.restaurant_id == restaurant_id,
#             func.cast(YandexReview.created_at, DATE) >= start_date,
#             func.cast(YandexReview.created_at, DATE) < end_date
#         ).count()

#         if total_reviews == 0:
#             return 0  # Если нет отзывов за месяц, NPS равен 0

#         # Количество Promoters (5 звезд)
#         promoters_count = session.query(YandexReview).filter(
#             YandexReview.restaurant_id == restaurant_id,
#             YandexReview.rating == 5,
#             func.cast(YandexReview.created_at, DATE) >= start_date,
#             func.cast(YandexReview.created_at, DATE) < end_date
#         ).count()

#         # Количество Detractors (1, 2, или 3 звезды)
#         detractors_count = session.query(YandexReview).filter(
#             YandexReview.restaurant_id == restaurant_id,
#             YandexReview.rating.in_([1, 2, 3]),
#             func.cast(YandexReview.created_at, DATE) >= start_date,
#             func.cast(YandexReview.created_at, DATE) < end_date
#         ).count()

#         # Рассчитываем проценты
#         promoters_percent = round((promoters_count / total_reviews) * 100, 1)
#         detractors_percent = round((detractors_count / total_reviews) * 100, 1)

#         # NPS = Promoters - Detractors
#         nps = round(promoters_percent - detractors_percent, 1)
#         return nps
#     except Exception as e:
#         session.rollback()
#         raise e


# def calculate_satisfaction_level(restaurant_id):
#     """Рассчитываем уровень удовлетворенности для ресторана."""
#     try:
#         total_reviews = count_rest_ya_reviews(restaurant_id=restaurant_id)

#         if total_reviews == 0:
#             return 0

#         # Количество положительных отзывов с позитивной семантикой
#         positive_reviews_count = session.query(YandexReview).filter(
#             YandexReview.restaurant_id == restaurant_id,
#             YandexReview.semantic.ilike("п")
#         ).count()

#         # Рассчитываем процент положительных отзывов
#         satisfaction_level = round((
#             positive_reviews_count / total_reviews
#         ) * 100, 1)
#         return satisfaction_level
#     except Exception as e:
#         session.rollback()
#         raise e

def calculate_nps(restaurant_id):
    """Рассчитываем NPS для ресторана, учитывая отзывы с Яндекса и 2ГИС."""
    try:
        # Получаем общее количество отзывов с обеих платформ
        total_reviews_ya = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id
        ).count()

        total_reviews_twogis = session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id
        ).count()

        total_reviews = total_reviews_ya + total_reviews_twogis

        if total_reviews == 0:
            return 0  # Если нет отзывов, NPS равен 0

        # Количество Promoters (5 звезд) на Яндексе
        promoters_ya_count = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            YandexReview.rating == 5
        ).count()

        # Количество Detractors (1, 2, или 3 звезды) на Яндексе
        detractors_ya_count = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            YandexReview.rating.in_([1, 2, 3])
        ).count()

        # Количество Promoters (5 звезд) на 2ГИС
        promoters_twogis_count = session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id,
            TwogisReview.rating == 5
        ).count()

        # Количество Detractors (1, 2, или 3 звезды) на 2ГИС
        detractors_twogis_count = session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id,
            TwogisReview.rating.in_([1, 2, 3])
        ).count()

        # Общее количество Promoters и Detractors
        total_promoters = promoters_ya_count + promoters_twogis_count
        total_detractors = detractors_ya_count + detractors_twogis_count

        # Рассчитываем проценты Promoters и Detractors
        promoters_percent = (total_promoters / total_reviews) * 100
        detractors_percent = (total_detractors / total_reviews) * 100

        # Рассчитываем NPS = Promoters - Detractors
        nps = round(promoters_percent - detractors_percent, 1)
        return nps

    except Exception as e:
        session.rollback()
        raise e


# def calculate_satisfaction_level_for_month(restaurant_id, year, month):
#     """Рассчитываем уровень удовлетворенности для ресторана за месяц."""
#     try:
#         start_date = datetime(year, month, 1)
#         end_date = datetime(
#             year, month + 1, 1
#         ) if month < 12 else datetime(year + 1, 1, 1)

#         total_reviews = session.query(YandexReview).filter(
#             YandexReview.restaurant_id == restaurant_id,
#             func.cast(YandexReview.created_at, DATE) >= start_date,
#             func.cast(YandexReview.created_at, DATE) < end_date
#         ).count()

#         if total_reviews == 0:
#             return 0

#         positive_reviews_count = session.query(YandexReview).filter(
#             YandexReview.restaurant_id == restaurant_id,
#             YandexReview.semantic.ilike("п"),
#             func.cast(YandexReview.created_at, DATE) >= start_date,
#             func.cast(YandexReview.created_at, DATE) < end_date
#         ).count()

#         # Рассчитываем процент положительных отзывов
#         satisfaction_level = round(
#             (positive_reviews_count / total_reviews) * 100, 1
#         )
#         return satisfaction_level
#     except Exception as e:
#         session.rollback()
#         raise e
def calculate_satisfaction_level_for_month(restaurant_id, year, month):
    """Рассчитываем уровень удовлетворенности для ресторана за месяц, учитывая отзывы с Яндекса и 2ГИС."""
    try:
        start_date = datetime(year, month, 1)
        end_date = datetime(
            year, month + 1, 1
        ) if month < 12 else datetime(year + 1, 1, 1)

        # Получаем общее количество отзывов с Яндекса
        total_reviews_ya = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            func.cast(YandexReview.created_at, DATE) >= start_date,
            func.cast(YandexReview.created_at, DATE) < end_date
        ).count()

        # Получаем общее количество отзывов с 2ГИС
        total_reviews_twogis = session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id,
            func.cast(TwogisReview.created_at, DATE) >= start_date,
            func.cast(TwogisReview.created_at, DATE) < end_date
        ).count()

        total_reviews = total_reviews_ya + total_reviews_twogis

        if total_reviews == 0:
            return 0  # Если нет отзывов, уровень удовлетворенности равен 0

        # Положительные отзывы на Яндексе
        positive_reviews_count_ya = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            YandexReview.semantic.ilike("п"),
            func.cast(YandexReview.created_at, DATE) >= start_date,
            func.cast(YandexReview.created_at, DATE) < end_date
        ).count()

        # Положительные отзывы на 2ГИС
        positive_reviews_count_twogis = session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id,
            TwogisReview.semantic.ilike("п"),
            func.cast(TwogisReview.created_at, DATE) >= start_date,
            func.cast(TwogisReview.created_at, DATE) < end_date
        ).count()

        # Общие положительные отзывы
        positive_reviews_count = positive_reviews_count_ya + positive_reviews_count_twogis

        # Рассчитываем процент положительных отзывов
        satisfaction_level = round(
            (positive_reviews_count / total_reviews) * 100, 1
        )
        return satisfaction_level

    except Exception as e:
        session.rollback()
        raise e
