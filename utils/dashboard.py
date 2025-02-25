from datetime import datetime
from sqlalchemy import func
from sqlalchemy.types import Date as DATE
from api.db import session
from data.data_main import YandexReview


def count_rest_ya_reviews(restaurant_id):
    """Получаем количество отзывов с Яндекса определённого ресторана."""
    try:
        return session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id
        ).count()
    except Exception as e:
        session.rollback()
        raise e


def avg_rest_ya_rating(restaurant_id):
    """Получаем среднее значение рейтинга отзывов с Яндекса для ресторана."""
    try:
        return session.query(func.avg(YandexReview.rating)).filter(
            YandexReview.restaurant_id == restaurant_id
        ).scalar()
    except Exception as e:
        session.rollback()
        raise e


def calculate_nps(restaurant_id):
    """Рассчитываем NPS для ресторана."""
    try:
        total_reviews = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id
        ).count()

        if total_reviews == 0:
            return 0

        # Количество Promoters (5 звезд)
        promoters_count = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            YandexReview.rating == 5
        ).count()

        # Количество Detractors (1, 2, или 3 звезды)
        detractors_count = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            YandexReview.rating.in_([1, 2, 3])
        ).count()

        # Рассчитываем проценты
        promoters_percent = (promoters_count / total_reviews) * 100
        detractors_percent = (detractors_count / total_reviews) * 100

        # NPS = Promoters - Detractors
        nps = round(promoters_percent - detractors_percent, 1)
        return nps
    except Exception as e:
        session.rollback()
        raise e


def calculate_nps_for_month(restaurant_id, year, month):
    """Рассчитываем NPS для ресторана за конкретный месяц."""
    try:
        start_date = datetime(year, month, 1)
        end_date = datetime(
            year, month + 1, 1
        ) if month < 12 else datetime(year + 1, 1, 1)

        total_reviews = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            func.cast(YandexReview.created_at, DATE) >= start_date,
            func.cast(YandexReview.created_at, DATE) < end_date
        ).count()

        if total_reviews == 0:
            return 0  # Если нет отзывов за месяц, NPS равен 0

        # Количество Promoters (5 звезд)
        promoters_count = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            YandexReview.rating == 5,
            func.cast(YandexReview.created_at, DATE) >= start_date,
            func.cast(YandexReview.created_at, DATE) < end_date
        ).count()

        # Количество Detractors (1, 2, или 3 звезды)
        detractors_count = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            YandexReview.rating.in_([1, 2, 3]),
            func.cast(YandexReview.created_at, DATE) >= start_date,
            func.cast(YandexReview.created_at, DATE) < end_date
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
        total_reviews = count_rest_ya_reviews(restaurant_id=restaurant_id)

        if total_reviews == 0:
            return 0

        # Количество положительных отзывов с позитивной семантикой
        positive_reviews_count = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            YandexReview.semantic.ilike("п")
        ).count()

        # Рассчитываем процент положительных отзывов
        satisfaction_level = (positive_reviews_count / total_reviews) * 100
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

        total_reviews = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            func.cast(YandexReview.created_at, DATE) >= start_date,
            func.cast(YandexReview.created_at, DATE) < end_date
        ).count()

        if total_reviews == 0:
            return 0

        positive_reviews_count = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            YandexReview.semantic.ilike("п"),
            func.cast(YandexReview.created_at, DATE) >= start_date,
            func.cast(YandexReview.created_at, DATE) < end_date
        ).count()

        # Рассчитываем процент положительных отзывов
        satisfaction_level = round(
            (positive_reviews_count / total_reviews) * 100, 1
        )
        return satisfaction_level
    except Exception as e:
        session.rollback()
        raise e
