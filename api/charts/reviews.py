from flask import Blueprint, jsonify, request
from sqlalchemy.orm import joinedload
from datetime import datetime

from data_base.data_main import YandexReview

trend_reviews_bp = Blueprint('trend_reviews', __name__)


@trend_reviews_bp.route('/trend-reviews', methods=['GET'])
def trend_reviews():
    user_id = request.args.get('user_id')  # Получаем user_id, который совпадает с restaurant_id
    if not user_id:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан user_id"
        }), 400

    # Получаем текущую дату
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Пример запроса, чтобы получить отзывы по restaurant_id (user_id)
    reviews = YandexReview.query.filter(
        YandexReview.restaurant_id == user_id
    ).all()

    # Если нет отзывов, возвращаем пустой ответ
    if not reviews:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Отзывы не найдены"
        }), 404

    # Данные для графика (по месяцам)
    months_data = {"Январь": 0, "Февраль": 0, "Март": 0, "Апрель": 0}
    for review in reviews:
        review_date = datetime.strptime(review.created_at, "%Y-%m-%d")  # Предполагаем формат даты: YYYY-MM-DD
        month_name = review_date.strftime("%B")  # Месяц в виде строки, например, Январь
        if month_name in months_data:
            months_data[month_name] += review.rating  # Суммируем рейтинг для каждого месяца

    # Переходим к подготовке данных для графика
    data = {
        "labels": list(months_data.keys()),
        "dataset": {
            "label": "Отзывы",
            "data": list(months_data.values()),
            "borderColor": "#36A2EB"
        }
    }

    return jsonify({
        "success": True,
        "data": data,
        "message": "Данные по trend-reviews получены"
    }), 200

# @trend_reviews_bp.route('/trend-reviews', methods=['GET'])
# def trend_reviews():
#     user_id = request.args.get('user_id')
#     if not user_id:
#         return jsonify({
#             "success": False,
#             "data": None,
#             "message": "Не указан user_id"
#         }), 400

#     data = {
#         "labels": ["Январь", "Февраль", "Март", "Апрель"],
#         "dataset": {
#             "label": "Отзывы",
#             "data": [100, 120, 140, 160],
#             "borderColor": "#36A2EB"
#         }
#     }

#     return jsonify({
#         "success": True,
#         "data": data,
#         "message": "Данные по trend-reviews получены"
#     }), 200


total_reviews_bp = Blueprint('total_reviews', __name__)


@total_reviews_bp.route('/total-reviews', methods=['GET'])
def total_reviews():
    user_id = int(request.args.get('user_id'))
    if not user_id:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан user_id"
        }), 400

    if user_id == 1:
        total_reviews = 234
        percentage_change = 100.2

    if user_id == 2:
        total_reviews = 432
        percentage_change = 30.2

    return jsonify({
        "success": True,
        "data": {
            "total_reviews": total_reviews,
            "percentage_change": percentage_change
        },
        "message": "Данные по total-reviews получены"
    }), 200
