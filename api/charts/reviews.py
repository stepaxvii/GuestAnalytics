from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from data_base.data_main import YandexReview, session

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

    # Пример запроса, чтобы получить отзывы по restaurant_id (user_id)
    reviews = session.query(YandexReview).filter(
        YandexReview.restaurant_id == user_id
    ).all()

    # Если нет отзывов, возвращаем пустой ответ
    if not reviews:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Отзывы не найдены"
        }), 404

    # Получаем текущую дату
    current_date = datetime.now()

    # Получаем текущий год и месяц в формате 'yyyy-mm'
    current_month = current_date.strftime("%Y-%m")

    # Генерируем список последних 4 месяцев в формате 'yyyy-mm'
    months = [current_month]
    for i in range(1, 4):
        # Используем relativedelta для точного вычитания месяцев
        prev_month_date = current_date - relativedelta(months=i)
        prev_month = prev_month_date.strftime("%Y-%m")  # Форматируем как 'yyyy-mm'
        months.append(prev_month)

    # Создаем словарь для хранения суммарных рейтингов по месяцам
    months_data = {month: 0 for month in months}

    # Перебираем все отзывы
    for review in reviews:
        # Преобразуем строку в datetime (формат даты 'YYYY-MM-DD')
        review_date = datetime.strptime(review.created_at, "%Y-%m-%d")

        # Получаем месяц и год отзыва в формате 'yyyy-mm'
        review_month = review_date.strftime("%Y-%m")

        # Если месяц отзыва есть в нашем списке, увеличиваем счетчик
        if review_month in months_data:
            months_data[review_month] += 1

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
