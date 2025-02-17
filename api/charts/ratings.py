from datetime import datetime
from dateutil.relativedelta import relativedelta

from flask import Blueprint, jsonify, request
from sqlalchemy import func
from api.db import session
from data.data_main import YandexReview
from sqlalchemy.exc import SQLAlchemyError

ratings_distribution_bp = Blueprint('ratings_distribution', __name__)


@ratings_distribution_bp.route('/ratings-distribution', methods=['GET'])
def ratings_distribution():
    restaurant_id = request.args.get('restaurant_id')
    if not restaurant_id:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан restaurant_id"
        }), 400

    # Получаем текущую дату
    current_date = datetime.now()
    current_month = current_date.strftime("%Y-%m")

    try:
        # Используем SQL-функцию to_date для преобразования строки в дату
        reviews = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            func.to_char(
                func.to_date(YandexReview.created_at, 'YYYY-MM-DD'), 'YYYY-MM'
            ) == current_month
        ).all()

        # Считаем количество отзывов по каждому рейтингу
        ratings_count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            if review.rating in ratings_count:
                ratings_count[review.rating] += 1

        # Общее количество отзывов
        total_reviews = sum(ratings_count.values())

        if total_reviews == 0:
            data = {
                "labels": ["★", "★★", "★★★", "★★★★", "★★★★★"],
                "values": [0, 0, 0, 0, 0]
            }
        else:
            data = {
                "labels": ["★", "★★", "★★★", "★★★★", "★★★★★"],
                "values": [
                    round((ratings_count[1] / total_reviews) * 100, 1),
                    round((ratings_count[2] / total_reviews) * 100, 1),
                    round((ratings_count[3] / total_reviews) * 100, 1),
                    round((ratings_count[4] / total_reviews) * 100, 1),
                    round((ratings_count[5] / total_reviews) * 100, 1)
                ]
            }

        # Закрываем транзакцию
        session.commit()

        return jsonify({
            "success": True,
            "data": data,
            "message": "Данные по ratings-distribution получены"
        }), 200

    except SQLAlchemyError as e:
        # В случае ошибки откатываем изменения
        session.rollback()
        return jsonify({
            "success": False,
            "data": None,
            "message": f"Ошибка базы данных: {str(e)}"
        }), 500


ratings_trend_bp = Blueprint('ratings_trend', __name__)


@ratings_trend_bp.route('/ratings-trend', methods=['GET'])
def ratings_trend():
    restaurant_id = request.args.get('restaurant_id')
    if not restaurant_id:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан restaurant_id"
        }), 400

    # Получаем текущую дату
    current_date = datetime.now()

    # Генерируем список последних 4 месяцев
    months = []
    for i in range(3, -1, -1):
        prev_month_date = current_date - relativedelta(months=i)
        prev_month = prev_month_date.strftime("%Y-%m")
        months.append(prev_month)

    # Словарь для хранения количества отзывов по месяцам
    ratings_count_by_month = {
        month: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0} for month in months
    }

    try:
        # Пример запроса для получения отзывов по restaurant_id
        reviews = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id
        ).all()

        # Перебираем все отзывы и считаем количество по месяцам
        for review in reviews:
            review_date = datetime.strptime(review.created_at, "%Y-%m-%d")
            review_month = review_date.strftime("%Y-%m")
            if review_month in ratings_count_by_month:
                rating = review.rating
                if rating in ratings_count_by_month[review_month]:
                    ratings_count_by_month[review_month][rating] += 1

        # Подготовка данных для графика
        data = {
            "labels": months,
            "datasets": [
                {
                    "label": "5 звёзд",
                    "data": [
                        ratings_count_by_month[month][5] for month in months
                    ],
                    "borderColor": "#2ECC71"
                },
                {
                    "label": "4 звезды",
                    "data": [
                        ratings_count_by_month[month][4] for month in months
                    ],
                    "borderColor": "#3498DB"
                },
                {
                    "label": "3 звезды",
                    "data": [
                        ratings_count_by_month[month][3] for month in months
                    ],
                    "borderColor": "#9B59B6"
                },
                {
                    "label": "2 звезды",
                    "data": [
                        ratings_count_by_month[month][2] for month in months
                    ],
                    "borderColor": "#F1C40F"
                },
                {
                    "label": "1 звезда",
                    "data": [
                        ratings_count_by_month[month][1] for month in months
                    ],
                    "borderColor": "#E74C3C"
                }
            ]
        }

        # Закрываем транзакцию
        session.commit()

        return jsonify({
            "success": True,
            "data": data,
            "message": "Данные по ratings-trend получены"
        }), 200

    except SQLAlchemyError as e:
        # Откатываем транзакцию при ошибке
        session.rollback()
        return jsonify({
            "success": False,
            "data": None,
            "message": f"Ошибка базы данных: {str(e)}"
        }), 500
