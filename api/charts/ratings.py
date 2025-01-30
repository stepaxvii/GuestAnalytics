from datetime import datetime

from flask import Blueprint, jsonify, request
from sqlalchemy import func

from data_base.data_main import YandexReview, session

ratings_distribution_bp = Blueprint('ratings_distribution', __name__)


@ratings_distribution_bp.route('/ratings-distribution', methods=['GET'])
def ratings_distribution():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан user_id"
        }), 400

    # Получаем текущую дату
    current_date = datetime.now()
    current_month = current_date.strftime("%Y-%m")

    # Получаем количество отзывов в текущем месяце для указанного restaurant_id (user_id)
    reviews = session.query(YandexReview).filter(
        YandexReview.restaurant_id == user_id,
        func.strftime('%Y-%m', YandexReview.date) == current_month  # Фильтрация по текущему месяцу
    ).all()

    # Считаем количество отзывов по каждому рейтингу
    ratings_count = {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0
    }

    for review in reviews:
        if review.rating in ratings_count:
            ratings_count[review.rating] += 1

    # Общее количество отзывов
    total_reviews = sum(ratings_count.values())

    # Если отзывов нет, возвращаем 0% для всех рейтингов
    if total_reviews == 0:
        data = {
            "labels": ["★☆☆☆☆", "★★☆☆☆", "★★★☆☆", "★★★★☆", "★★★★★"],
            "values": [0, 0, 0, 0, 0]
        }
    else:
        # Рассчитываем проценты для каждого рейтинга
        data = {
            "labels": ["★☆☆☆☆", "★★☆☆☆", "★★★☆☆", "★★★★☆", "★★★★★"],
            "values": [
                (ratings_count[1] / total_reviews) * 100,
                (ratings_count[2] / total_reviews) * 100,
                (ratings_count[3] / total_reviews) * 100,
                (ratings_count[4] / total_reviews) * 100,
                (ratings_count[5] / total_reviews) * 100
            ]
        }

    return jsonify({
        "success": True,
        "data": data,
        "message": "Данные по ratings-distribution получены"
    }), 200


ratings_trend_bp = Blueprint('ratings_trend', __name__)


@ratings_trend_bp.route('/ratings-trend', methods=['GET'])
def ratings_trend():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан user_id"
        }), 400

    data = {
        "labels": ["Январь", "Февраль", "Март", "Апрель"],
        "datasets": [
            {
                "label": "5 звёзд",
                "data": [20, 22, 25, 27],
                "borderColor": "#2ECC71"
            },
            {
                "label": "4 звезды",
                "data": [10, 14, 18, 20],
                "borderColor": "#3498DB"
            },
            {
                "label": "3 звезды",
                "data": [5, 7, 9, 6],
                "borderColor": "#9B59B6"
            },
            {
                "label": "2 звезды",
                "data": [3, 2, 4, 5],
                "borderColor": "#F1C40F"
            },
            {
                "label": "1 звезда",
                "data": [2, 3, 1, 2],
                "borderColor": "#E74C3C"
            }
        ]
    }

    return jsonify({
        "success": True,
        "data": data,
        "message": "Данные по ratings-trend получены"
    }), 200
