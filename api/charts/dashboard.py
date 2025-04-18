import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

from flask import Blueprint, jsonify, request
from sqlalchemy import func
from api.db import session
from data.data_main import TwogisReview, YandexReview
from data.read_data import (
    read_rest_ya_reviews,
    read_rest_month_insight_list,
    read_restaurant_by_wp
)
from utils.dash import (
    avg_rest_ya_rating,
    calculate_nps,
    calculate_nps_for_month,
    calculate_satisfaction_level,
    calculate_satisfaction_level_for_month,
    count_reviews_last_year
)
from utils.date import month_dict_dash

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

            # Получаем строковое представление месяца
            month_str = month_start.strftime("%m")

            # Если месяц — январь, заменяем "янв" на текущий год
            if month_dict_dash[month_str] == "янв":
                labels.insert(0, month_start.strftime("%Y"))
            else:
                labels.insert(0, f"{month_dict_dash[month_str]}")

            # Логируем текущий месяц
            logger.info(f"Обрабатываем месяц: {month_start.strftime('%Y-%m')}")

            # Формируем год-месяц для фильтрации
            year_month = month_start.strftime('%Y-%m')

            # Получаем количество отзывов за месяц для обеих таблиц
            reviews_in_month_yandex = session.query(YandexReview).filter(
                YandexReview.restaurant_id == restaurant_id,
                func.substring(YandexReview.created_at, 1, 7) == year_month
            ).count()

            reviews_in_month_twogis = session.query(TwogisReview).filter(
                TwogisReview.restaurant_id == restaurant_id,
                func.substring(TwogisReview.created_at, 1, 7) == year_month
            ).count()

            # Суммируем количество отзывов
            reviews_in_month = (
                reviews_in_month_yandex + reviews_in_month_twogis
            )

            # Логируем количество отзывов
            logger.info(f"Отзывы за {year_month}: {reviews_in_month}")

            # Добавляем данные в список
            trend_reviews_data.insert(0, reviews_in_month)

            # Средний рейтинг за месяц для обеих таблиц
            avg_rating_month_yandex = session.query(
                func.round(func.avg(YandexReview.rating), 1)
            ).filter(
                YandexReview.restaurant_id == restaurant_id,
                func.substring(YandexReview.created_at, 1, 7) == year_month
            ).scalar() or 0

            avg_rating_month_twogis = session.query(
                func.round(func.avg(TwogisReview.rating), 1)
            ).filter(
                TwogisReview.restaurant_id == restaurant_id,
                func.substring(TwogisReview.created_at, 1, 7) == year_month
            ).scalar() or 0

            # Считаем средний рейтинг для обоих источников
            total_reviews_month = (
                reviews_in_month_yandex + reviews_in_month_twogis
            )
            total_rating = (avg_rating_month_yandex * reviews_in_month_yandex +
                            avg_rating_month_twogis * reviews_in_month_twogis)

            # Вычисляем общий средний рейтинг с учетом всех отзывов
            avg_rating_month = (
                total_rating / total_reviews_month
            ) if total_reviews_month > 0 else 0

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
                "kpi_yandex": {
                    "total_reviews_yandex": 100,
                    "average_rating_yandex": 4.2,
                    "nps_yandex": 15,
                    "sentiment_percent_yandex": 60,
                },
                "kpi_twogis": {
                    "total_reviews_twogis": 50,
                    "average_rating_twogis": 4.0,
                    "nps_twogis": 10,
                    "sentiment_percent_twogis": 55,
                },
                "trend_reviews": {
                    "labels": labels,
                    "data": trend_reviews_data
                },
                "trend_reviews_yandex": {
                    "labels": labels,
                    "data": trend_reviews_data
                },
                "trend_reviews_twogis": {
                    "labels": labels,
                    "data": trend_reviews_data
                },
                "trend_rating": {
                    "labels": labels,
                    "data": trend_rating_data
                },
                "trend_rating_yandex": {
                    "labels": labels,
                    "data": trend_rating_data
                },
                "trend_rating_twogis": {
                    "labels": labels,
                    "data": trend_rating_data
                },
                "trend_nps": {
                    "labels": labels,
                    "data": trend_nps_data
                },
                "trend_nps_yandex": {
                    "labels": labels,
                    "data": trend_nps_data
                },
                "trend_nps_twogis": {
                    "labels": labels,
                    "data": trend_nps_data
                },
                "trend_sentiment": {
                    "labels": labels,
                    "data": trend_sentiment_data
                },
                "trend_sentiment_yandex": {
                    "labels": labels,
                    "data": trend_sentiment_data
                },
                "trend_sentiment_twogis": {
                    "labels": labels,
                    "data": trend_sentiment_data
                },
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
