import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

from flask import Blueprint, jsonify, request
from sqlalchemy import func
from sqlalchemy.types import Date as DATE
from api.db import session
from data.data_main import YandexReview
from data.read_data import (
    read_rest_ya_reviews,
    read_rest_month_insight_list,
    read_restaurant_by_wp
)
from utils.dashboard import (
    avg_rest_ya_rating,
    calculate_nps,
    calculate_nps_for_month,
    calculate_satisfaction_level,
    calculate_satisfaction_level_for_month,
    count_reviews_last_year
)
from utils.dashboard import month_dict

# Настройка логирования
logger = logging.getLogger()

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard', methods=['GET'])
def dashboard():
    wp_id = request.args.get('restaurant_id')
    if not wp_id:
        logger.error('Не указан wp_id')
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан wp_id"
        }), 400

    try:
        # Запрашиваем отзывы для определённого ресторана
        rest_data = read_restaurant_by_wp(wp_id=wp_id)
        restaurant_id = rest_data['id']
        reviews = read_rest_ya_reviews(restaurant_id=restaurant_id)

        # Если нет отзывов, возвращаем пустой ответ
        if not reviews:
            logger.warning(
                f"Отзывы для ресторана id: {wp_id} не найдены"
            )
            return jsonify({
                "success": False,
                "data": None,
                "message": "Мы трудимся над анализом отзывов. "
                "Обычно это занимает от 10 до 60 минут."
            }), 404

        # Общее количество отзывов за всё время
        total_reviews = count_reviews_last_year(restaurant_id=restaurant_id)
        # Среднее значение рейтинга за всё время
        average_rating = avg_rest_ya_rating(restaurant_id=restaurant_id)
        # Процент лояльных гостей (NPS)
        nps = calculate_nps(restaurant_id=restaurant_id)
        # Процент положительных отзывов
        sentiment_percent = calculate_satisfaction_level(
            restaurant_id=restaurant_id
        )

        # AI инсайты за последний полный месяц
        ai_insights = read_rest_month_insight_list(restaurant_id=restaurant_id)

        # Тренды за последние 12 месяцев
        labels = []
        trend_reviews_data = []
        trend_rating_data = []
        trend_nps_data = []
        trend_sentiment_data = []

        today = datetime.today()
        for i in range(12):  # За последние 12 месяцев
            month_start = today - relativedelta(months=i)

            # Используем словарь для перевода месяца в русский формат
            month_str = month_start.strftime("%m")
            # Если месяц — январь, заменяем "янв" на текущий год
            if month_dict[month_str] == "янв":
                # Вставляем год в формате "гггг"
                labels.insert(0, month_start.strftime("%Y"))
            else:
                # Вставляем сокращённое название месяца
                labels.insert(0, f"{month_dict[month_str]}")

            # Получаем количество отзывов за месяц
            # reviews_in_month = session.query(YandexReview).filter(
            #     YandexReview.restaurant_id == restaurant_id,
            #     func.cast(
            #         YandexReview.created_at, DATE
            #     ) >= month_start.replace(day=1),
            #     func.cast(YandexReview.created_at, DATE) < (
            #         month_start + relativedelta(months=1)
            #     ).replace(day=1)
            # ).count()

            # Получаем количество отзывов за месяц
            # Логируем текущий месяц
            logger.debug(f"Обрабатываем месяц: {month_start.strftime('%Y-%m')}")
            logger.debug(f"Запрос отзывов за период: {month_start.replace(day=1)} до {(month_start + relativedelta(months=1)).replace(day=1)}")

            reviews_in_month = session.query(YandexReview).filter(
                YandexReview.restaurant_id == restaurant_id,
                func.cast(YandexReview.created_at, DATE) >= month_start.replace(day=1),
                func.cast(YandexReview.created_at, DATE) < (month_start + relativedelta(months=1)).replace(day=1)
            ).count()
            logger.debug(f"Отзывы за апрель: {reviews_in_month}")
            trend_reviews_data.insert(0, reviews_in_month)

            # Средний рейтинг за месяц
            avg_rating_month = session.query(
                func.round(func.avg(YandexReview.rating), 1)
            ).filter(
                YandexReview.restaurant_id == restaurant_id,
                func.cast(
                    YandexReview.created_at, DATE
                ) >= month_start.replace(day=1),
                func.cast(YandexReview.created_at, DATE) < (
                    month_start + relativedelta(months=1)
                ).replace(day=1)
            ).scalar() or 0
            trend_rating_data.insert(0, avg_rating_month)

            # NPS за месяц
            nps_month = calculate_nps_for_month(
                restaurant_id, month_start.year, month_start.month
            )
            trend_nps_data.insert(0, nps_month)

            # Уровень удовлетворенности за месяц
            satisfaction_month = calculate_satisfaction_level_for_month(
                restaurant_id, month_start.year, month_start.month
            )
            trend_sentiment_data.insert(0, satisfaction_month)

        return jsonify({
            "success": True,
            "data": {
                "kpi": {
                    "total_reviews": total_reviews,
                    "average_rating": average_rating,
                    "nps": nps,
                    "sentiment_percent": sentiment_percent,
                    "ai_insights": ai_insights,
                },
                "trend_reviews": {
                    "labels": labels,
                    "data": trend_reviews_data
                },
                "trend_rating": {
                    "labels": labels,
                    "data": trend_rating_data
                },
                "trend_nps": {
                    "labels": labels,
                    "data": trend_nps_data
                },
                "trend_sentiment": {
                    "labels": labels,
                    "data": trend_sentiment_data
                }
            }
        })

    except Exception as e:
        logger.error(f"Ошибка при обработке запроса: {e}")
        session.rollback()
        return jsonify({
            "success": False,
            "data": None,
            "message": "Произошла ошибка при обработке запроса.\n"
            "Обратитель в поддержку."
        }), 500
