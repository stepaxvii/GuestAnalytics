from datetime import datetime
from sqlalchemy import func
from sqlalchemy.types import Date as DATE
from api.db import session
from data.data_main import YandexReview, TwogisReview


def count_rest_reviews(restaurant_id):
    """Получаем общее количество отзывов для ресторана с Яндекса и TwoGIS."""
    try:
        yandex_reviews_count = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id
        ).count()

        twogis_reviews_count = session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id
        ).count()

        return yandex_reviews_count + twogis_reviews_count
    except Exception as e:
        session.rollback()
        raise e


def count_reviews_last_year(restaurant_id):
    """
    Получаем общее количество отзывов за последний год с Яндекса и TwoGIS.
    """
    try:
        # Текущая дата
        current_date = datetime.now()

        # Дата год назад
        start_date = current_date.replace(year=current_date.year - 1, day=1)

        # Преобразуем обе даты в формат "YYYY-MM"
        current_month_str = current_date.strftime("%Y-%m")
        start_month_str = start_date.strftime("%Y-%m")

        # Подсчитываем количество отзывов с Яндекса
        yandex_reviews = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            func.substr(YandexReview.created_at, 1, 7) >= start_month_str,
            func.substr(YandexReview.created_at, 1, 7) <= current_month_str
        ).count()

        # Подсчитываем количество отзывов с TwoGIS
        twogis_reviews = session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id,
            func.substr(TwogisReview.created_at, 1, 7) >= start_month_str,
            func.substr(TwogisReview.created_at, 1, 7) <= current_month_str
        ).count()

        total_reviews = yandex_reviews + twogis_reviews
        return total_reviews, yandex_reviews, twogis_reviews
    except Exception as e:
        session.rollback()
        raise e


def avg_rest_rating(restaurant_id):
    """Получаем средний рейтинг отзывов с Яндекса и TwoGIS для ресторана."""
    try:
        yandex_avg_rating = session.query(
            func.avg(YandexReview.rating)
        ).filter(
            YandexReview.restaurant_id == restaurant_id
        ).scalar() or 0

        twogis_avg_rating = session.query(
            func.avg(TwogisReview.rating)
        ).filter(
            TwogisReview.restaurant_id == restaurant_id
        ).scalar() or 0

        # Возвращаем среднее значение рейтинга
        total_reviews = count_rest_reviews(restaurant_id)

        average_rating = round((yandex_avg_rating + twogis_avg_rating) / 2, 1)
        yandex_avg_rating = round(yandex_avg_rating, 1)
        twogis_avg_rating = round(twogis_avg_rating, 1)
        if total_reviews == 0:
            return 0, 0, 0
        return average_rating, yandex_avg_rating, twogis_avg_rating
    except Exception as e:
        session.rollback()
        raise e


def calculate_nps(restaurant_id):
    """Рассчитываем общий NPS, а также отдельно для Яндекса и TwoGIS."""
    try:
        total_yandex_reviews = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id
        ).count()

        total_twogis_reviews = session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id
        ).count()

        total_reviews = total_yandex_reviews + total_twogis_reviews

        if total_reviews == 0:
            return {
                'overall_nps': 0,
                'yandex_nps': 0,
                'twogis_nps': 0
            }

        # Яндекс
        yandex_promoters = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            YandexReview.rating == 5
        ).count()

        yandex_detractors = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            YandexReview.rating.in_([1, 2, 3])
        ).count()

        if total_yandex_reviews > 0:
            yandex_nps = round(
                (
                    yandex_promoters - yandex_detractors
                ) / total_yandex_reviews * 100, 1)
        else:
            yandex_nps = 0

        # TwoGIS
        twogis_promoters = session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id,
            TwogisReview.rating == 5
        ).count()

        twogis_detractors = session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id,
            TwogisReview.rating.in_([1, 2, 3])
        ).count()

        if total_twogis_reviews > 0:
            twogis_nps = round(
                (
                    twogis_promoters - twogis_detractors
                ) / total_twogis_reviews * 100, 1)
        else:
            twogis_nps = 0

        # Общий NPS
        total_promoters = yandex_promoters + twogis_promoters
        total_detractors = yandex_detractors + twogis_detractors

        overall_nps = round(
            (total_promoters - total_detractors) / total_reviews * 100, 1)

        return overall_nps, yandex_nps, twogis_nps

    except Exception as e:
        session.rollback()
        raise e


# def calculate_nps_for_month(restaurant_id, year, month):
#     """Рассчитываем NPS для ресторана за конкретный месяц (Яндекс + 2ГИС)."""
#     try:
#         start_date = datetime(year, month, 1)
#         end_date = datetime(
#             year, month + 1, 1
#         ) if month < 12 else datetime(year + 1, 1, 1)

#         # Общее количество отзывов за месяц
#         total_reviews = session.query(YandexReview).filter(
#             YandexReview.restaurant_id == restaurant_id,
#             func.cast(YandexReview.created_at, DATE) >= start_date,
#             func.cast(YandexReview.created_at, DATE) < end_date
#         ).count() + session.query(TwogisReview).filter(
#             TwogisReview.restaurant_id == restaurant_id,
#             func.cast(TwogisReview.created_at, DATE) >= start_date,
#             func.cast(TwogisReview.created_at, DATE) < end_date
#         ).count()

#         if total_reviews == 0:
#             return 0  # Если нет отзывов за месяц, NPS равен 0

#         # Количество Promoters (5 звезд)
#         promoters_count = session.query(YandexReview).filter(
#             YandexReview.restaurant_id == restaurant_id,
#             YandexReview.rating == 5,
#             func.cast(YandexReview.created_at, DATE) >= start_date,
#             func.cast(YandexReview.created_at, DATE) < end_date
#         ).count() + session.query(TwogisReview).filter(
#             TwogisReview.restaurant_id == restaurant_id,
#             TwogisReview.rating == 5,
#             func.cast(TwogisReview.created_at, DATE) >= start_date,
#             func.cast(TwogisReview.created_at, DATE) < end_date
#         ).count()

#         # Количество Detractors (1, 2, или 3 звезды)
#         detractors_count = session.query(YandexReview).filter(
#             YandexReview.restaurant_id == restaurant_id,
#             YandexReview.rating.in_([1, 2, 3]),
#             func.cast(YandexReview.created_at, DATE) >= start_date,
#             func.cast(YandexReview.created_at, DATE) < end_date
#         ).count() + session.query(TwogisReview).filter(
#             TwogisReview.restaurant_id == restaurant_id,
#             TwogisReview.rating.in_([1, 2, 3]),
#             func.cast(TwogisReview.created_at, DATE) >= start_date,
#             func.cast(TwogisReview.created_at, DATE) < end_date
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

def calculate_nps_for_month(restaurant_id, year, month):
    """Рассчитывает NPS за указанный месяц (в целом, Яндекс и 2ГИС)."""
    try:
        # Преобразуем в строку YYYY-MM
        year_month = f"{year}-{month:02}"

        # Отзывы за месяц
        yandex_reviews = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            func.substring(YandexReview.created_at, 1, 7) == year_month
        )

        twogis_reviews = session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id,
            func.substring(TwogisReview.created_at, 1, 7) == year_month
        )

        yandex_promoters = yandex_reviews.filter(
            YandexReview.rating == 5
        ).count()
        yandex_detractors = yandex_reviews.filter(YandexReview.rating.in_([1, 2, 3])).count()
        total_yandex = yandex_reviews.count()

        twogis_promoters = twogis_reviews.filter(TwogisReview.rating == 5).count()
        twogis_detractors = twogis_reviews.filter(TwogisReview.rating.in_([1, 2, 3])).count()
        total_twogis = twogis_reviews.count()

        total = total_yandex + total_twogis
        total_promoters = yandex_promoters + twogis_promoters
        total_detractors = yandex_detractors + twogis_detractors

        nps = round((total_promoters - total_detractors) / total * 100, 1) if total else 0
        yandex_nps = round((yandex_promoters - yandex_detractors) / total_yandex * 100, 1) if total_yandex else 0
        twogis_nps = round((twogis_promoters - twogis_detractors) / total_twogis * 100, 1) if total_twogis else 0

        return nps, yandex_nps, twogis_nps

    except Exception as e:
        session.rollback()
        raise e


def calculate_satisfaction_level(restaurant_id):
    """Рассчитываем уровень удовлетворенности."""
    try:
        total_yandex_reviews = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id
        ).count()

        total_twogis_reviews = session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id
        ).count()

        total_reviews = total_yandex_reviews + total_twogis_reviews

        if total_reviews == 0:
            return {
                'overall_satisfaction': 0,
                'yandex_satisfaction': 0,
                'twogis_satisfaction': 0
            }

        # Положительные отзывы
        yandex_positive = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            YandexReview.semantic.ilike("п")
        ).count()

        twogis_positive = session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id,
            TwogisReview.semantic.ilike("п")
        ).count()

        # Расчёты
        if total_yandex_reviews > 0:
            yandex_satisfaction = round(
                yandex_positive / total_yandex_reviews * 100, 1)
        else:
            yandex_satisfaction = 0

        if total_twogis_reviews > 0:
            twogis_satisfaction = round(
                twogis_positive / total_twogis_reviews * 100, 1)
        else:
            twogis_satisfaction = 0

        overall_satisfaction = round(
            (yandex_positive + twogis_positive) / total_reviews * 100, 1)

        return overall_satisfaction, yandex_satisfaction, twogis_satisfaction

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

#         # Общее количество отзывов за месяц
#         total_reviews = session.query(YandexReview).filter(
#             YandexReview.restaurant_id == restaurant_id,
#             func.cast(YandexReview.created_at, DATE) >= start_date,
#             func.cast(YandexReview.created_at, DATE) < end_date
#         ).count() + session.query(TwogisReview).filter(
#             TwogisReview.restaurant_id == restaurant_id,
#             func.cast(TwogisReview.created_at, DATE) >= start_date,
#             func.cast(TwogisReview.created_at, DATE) < end_date
#         ).count()

#         if total_reviews == 0:
#             return 0

#         positive_reviews_count = session.query(YandexReview).filter(
#             YandexReview.restaurant_id == restaurant_id,
#             YandexReview.semantic.ilike("п"),
#             func.cast(YandexReview.created_at, DATE) >= start_date,
#             func.cast(YandexReview.created_at, DATE) < end_date
#         ).count() + session.query(TwogisReview).filter(
#             TwogisReview.restaurant_id == restaurant_id,
#             TwogisReview.semantic.ilike("п"),
#             func.cast(TwogisReview.created_at, DATE) >= start_date,
#             func.cast(TwogisReview.created_at, DATE) < end_date
#         ).count()

#         satisfaction_level = round(
#             (positive_reviews_count / total_reviews) * 100, 1
#         )
#         return satisfaction_level
#     except Exception as e:
#         session.rollback()
#         raise e

def calculate_satisfaction_level_for_month(restaurant_id, year, month):
    """Рассчитывает уровень удовлетворенности за месяц (в целом, Яндекс и 2ГИС)."""
    try:
        year_month = f"{year}-{month:02}"

        yandex_reviews = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            func.substring(YandexReview.created_at, 1, 7) == year_month
        )

        twogis_reviews = session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id,
            func.substring(TwogisReview.created_at, 1, 7) == year_month
        )

        total_yandex = yandex_reviews.count()
        total_twogis = twogis_reviews.count()

        yandex_positive = yandex_reviews.filter(YandexReview.semantic.ilike("п")).count()
        twogis_positive = twogis_reviews.filter(TwogisReview.semantic.ilike("п")).count()

        total = total_yandex + total_twogis

        overall = round((yandex_positive + twogis_positive) / total * 100, 1) if total else 0
        yandex_score = round(yandex_positive / total_yandex * 100, 1) if total_yandex else 0
        twogis_score = round(twogis_positive / total_twogis * 100, 1) if total_twogis else 0

        return overall, yandex_score, twogis_score

    except Exception as e:
        session.rollback()
        raise e
