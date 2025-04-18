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


def avg_rest_ya_rating(restaurant_id):
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
        if total_reviews == 0:
            return 0
        return round((yandex_avg_rating + twogis_avg_rating) / 2, 1)
    except Exception as e:
        session.rollback()
        raise e


def calculate_nps(restaurant_id):
    """Рассчитываем NPS для ресторана с Яндекса и TwoGIS."""
    try:
        total_reviews = count_rest_reviews(restaurant_id)

        if total_reviews == 0:
            return 0

        # Количество Promoters (5 звезд) для Яндекса
        yandex_promoters = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            YandexReview.rating == 5
        ).count()

        # Количество Promoters (5 звезд) для TwoGIS
        twogis_promoters = session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id,
            TwogisReview.rating == 5
        ).count()

        # Количество Detractors (1, 2, или 3 звезды) для Яндекса
        yandex_detractors = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            YandexReview.rating.in_([1, 2, 3])
        ).count()

        # Количество Detractors (1, 2, или 3 звезды) для TwoGIS
        twogis_detractors = session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id,
            TwogisReview.rating.in_([1, 2, 3])
        ).count()

        # Рассчитываем проценты
        promoters_percent = (
            yandex_promoters + twogis_promoters
        ) / total_reviews * 100
        detractors_percent = (
            yandex_detractors + twogis_detractors
        ) / total_reviews * 100

        # NPS = Promoters - Detractors
        nps = round(promoters_percent - detractors_percent, 1)
        return nps
    except Exception as e:
        session.rollback()
        raise e


def calculate_nps_for_month(restaurant_id, year, month):
    """Рассчитываем NPS для ресторана за конкретный месяц (Яндекс + 2ГИС)."""
    try:
        start_date = datetime(year, month, 1)
        end_date = datetime(
            year, month + 1, 1
        ) if month < 12 else datetime(year + 1, 1, 1)

        # Общее количество отзывов за месяц
        total_reviews = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            func.cast(YandexReview.created_at, DATE) >= start_date,
            func.cast(YandexReview.created_at, DATE) < end_date
        ).count() + session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id,
            func.cast(TwogisReview.created_at, DATE) >= start_date,
            func.cast(TwogisReview.created_at, DATE) < end_date
        ).count()

        if total_reviews == 0:
            return 0  # Если нет отзывов за месяц, NPS равен 0

        # Количество Promoters (5 звезд)
        promoters_count = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            YandexReview.rating == 5,
            func.cast(YandexReview.created_at, DATE) >= start_date,
            func.cast(YandexReview.created_at, DATE) < end_date
        ).count() + session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id,
            TwogisReview.rating == 5,
            func.cast(TwogisReview.created_at, DATE) >= start_date,
            func.cast(TwogisReview.created_at, DATE) < end_date
        ).count()

        # Количество Detractors (1, 2, или 3 звезды)
        detractors_count = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            YandexReview.rating.in_([1, 2, 3]),
            func.cast(YandexReview.created_at, DATE) >= start_date,
            func.cast(YandexReview.created_at, DATE) < end_date
        ).count() + session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id,
            TwogisReview.rating.in_([1, 2, 3]),
            func.cast(TwogisReview.created_at, DATE) >= start_date,
            func.cast(TwogisReview.created_at, DATE) < end_date
        ).count()

        # Рассчитываем проценты
        promoters_percent = round((promoters_count / total_reviews) * 100, 1)
        detractors_percent = round((detractors_count / total_reviews) * 100, 1)

        # NPS = Promoters - Detractors
        nps = round(promoters_percent - detractors_percent, 1)
        return nps
    except Exception as e:
        session.rollback()
        raise e


def calculate_satisfaction_level(restaurant_id):
    """Рассчитываем уровень удовлетворенности для ресторана."""
    try:
        total_reviews = count_rest_reviews(restaurant_id)

        if total_reviews == 0:
            return 0

        # Количество положительных отзывов с Яндекса
        yandex_positive_reviews = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            YandexReview.semantic.ilike("п")
        ).count()

        # Количество положительных отзывов с TwoGIS
        twogis_positive_reviews = session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id,
            TwogisReview.semantic.ilike("п")
        ).count()

        # Рассчитываем процент положительных отзывов
        satisfaction_level = round(
            (
                yandex_positive_reviews + twogis_positive_reviews
            ) / total_reviews * 100, 1
        )
        return satisfaction_level
    except Exception as e:
        session.rollback()
        raise e


def calculate_satisfaction_level_for_month(restaurant_id, year, month):
    """Рассчитываем уровень удовлетворенности для ресторана за месяц."""
    try:
        start_date = datetime(year, month, 1)
        end_date = datetime(
            year, month + 1, 1
        ) if month < 12 else datetime(year + 1, 1, 1)

        # Общее количество отзывов за месяц
        total_reviews = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            func.cast(YandexReview.created_at, DATE) >= start_date,
            func.cast(YandexReview.created_at, DATE) < end_date
        ).count() + session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id,
            func.cast(TwogisReview.created_at, DATE) >= start_date,
            func.cast(TwogisReview.created_at, DATE) < end_date
        ).count()

        if total_reviews == 0:
            return 0

        positive_reviews_count = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            YandexReview.semantic.ilike("п"),
            func.cast(YandexReview.created_at, DATE) >= start_date,
            func.cast(YandexReview.created_at, DATE) < end_date
        ).count() + session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id,
            TwogisReview.semantic.ilike("п"),
            func.cast(TwogisReview.created_at, DATE) >= start_date,
            func.cast(TwogisReview.created_at, DATE) < end_date
        ).count()

        satisfaction_level = round(
            (positive_reviews_count / total_reviews) * 100, 1
        )
        return satisfaction_level
    except Exception as e:
        session.rollback()
        raise e
