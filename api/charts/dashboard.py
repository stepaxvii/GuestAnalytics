import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

from flask import Blueprint, jsonify, request
from sqlalchemy import func
from api.db import session
from data.data_main import YandexReview
from data.read_data import read_rest_ya_reviews
from utils.dashboard import (
    avg_rest_ya_rating,
    calculate_nps,
    calculate_nps_for_month,
    calculate_satisfaction_level,
    calculate_satisfaction_level_for_month,
    count_rest_ya_reviews
)
from utils.date import month_dict

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard', method='GET')
def dashboard():
    restaurant_id = request.args.get('restaurant_id')
    if not restaurant_id:
        logging.error('Не указан restaurant_id')
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан restaurant_id"
        }), 400

    try:
        # Запрашиваем все отзывы для определённого ресторана
        reviews = read_rest_ya_reviews(restaurant_id=restaurant_id)

        # Если нет отзывов, возвращаем пустой ответ
        if not reviews:
            logging.warning(
                f"Отзывы для ресторана id: {restaurant_id} не найдены"
            )
            return jsonify({
                "success": False,
                "data": None,
                "message": "Отзывы не найдены"
            }), 404

        # Общее количество отзывов за всё время
        total_reviews = count_rest_ya_reviews(restaurant_id=restaurant_id)
        # Среднее значение рейтинга за всё время
        average_rating = avg_rest_ya_rating(restaurant_id=restaurant_id)
        # Процент лояльных гостей (NPS)
        nps = calculate_nps(restaurant_id=restaurant_id)
        # Процент положительных отзывов
        sentiment_percent = calculate_satisfaction_level(
            restaurant_id=restaurant_id
        )

        # Сгенерируем фиктивные "AI Insights"
        ai_insights = [
            "Инсайт 1: Это может помочь улучшить обслуживание.",
            "Инсайт 2: Возможно, стоит улучшить качество еды.",
            "Инсайт 3: Проверьте отзывы с низким рейтингом для улучшений.",
        ]

        # Тренды за последние 12 месяцев
        labels = []
        trend_reviews_data = []
        trend_rating_data = []
        trend_nps_data = []
        trend_sentiment_data = []

        today = datetime.today()
        for i in range(12):  # За последние 12 месяцев
            month_start = today - relativedelta(months=i)
            labels.append(month_start.strftime("%b %Y"))

            # Получаем количество отзывов за месяц
            reviews_in_month = session.query(YandexReview).filter(
                YandexReview.restaurant_id == restaurant_id,
                YandexReview.created_at >= month_start.replace(day=1),
                YandexReview.created_at < (
                    month_start + relativedelta(months=1)
                ).replace(day=1)
            ).count()
            trend_reviews_data.append(reviews_in_month)

            # Средний рейтинг за месяц
            avg_rating_month = session.query(
                func.avg(YandexReview.rating)
            ).filter(
                YandexReview.restaurant_id == restaurant_id,
                YandexReview.created_at >= month_start.replace(day=1),
                YandexReview.created_at < (
                    month_start + relativedelta(months=1)
                ).replace(day=1)
            ).scalar() or 0
            trend_rating_data.append(avg_rating_month)

            # NPS за месяц
            nps_month = calculate_nps_for_month(
                restaurant_id, month_start.year, month_start.month
            )
            trend_nps_data.append(nps_month)

            # Уровень удовлетворенности за месяц
            satisfaction_month = calculate_satisfaction_level_for_month(
                restaurant_id, month_start.year, month_start.month
            )
            trend_sentiment_data.append(satisfaction_month)

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
        logging.error(f"Ошибка при обработке запроса: {e}")
        return jsonify({
            "success": False,
            "data": None,
            "message": "Произошла ошибка при обработке запроса"
        }), 500
