from datetime import datetime
from dateutil.relativedelta import relativedelta

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

    # Получаем количество отзывов в текущем месяце
    # для указанного restaurant_id (user_id),
    # фильтруя по текущему месяцу
    reviews = session.query(YandexReview).filter(
        YandexReview.restaurant_id == user_id,
        func.strftime('%Y-%m', YandexReview.created_at) == current_month
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
            "labels": ["★", "★★", "★★★", "★★★★", "★★★★★"],
            "values": [0, 0, 0, 0, 0]
        }
    else:
        # Рассчитываем проценты для каждого рейтинга
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

    # Получаем текущую дату
    current_date = datetime.now()

    # Генерируем список последних 4 месяцев в формате 'yyyy-mm'
    months = []
    # Сначала добавляем старые месяцы, начиная с 3
    for i in range(3, -1, -1):
        # Используем relativedelta для точного вычитания месяцев
        prev_month_date = current_date - relativedelta(months=i)
        # Форматируем как 'yyyy-mm'
        prev_month = prev_month_date.strftime("%Y-%m")
        months.append(prev_month)

    # Создаем словарь для хранения количества отзывов
    ratings_count_by_month = {
        month: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0} for month in months
    }

    # Пример запроса, чтобы получить отзывы по restaurant_id (user_id)
    reviews = session.query(YandexReview).filter(
        YandexReview.restaurant_id == user_id
    ).all()

    # Перебираем все отзывы
    for review in reviews:
        # Преобразуем строку в datetime (формат даты 'YYYY-MM-DD')
        review_date = datetime.strptime(review.created_at, "%Y-%m-%d")

        # Получаем месяц и год отзыва в формате 'yyyy-mm'
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
                "data": [ratings_count_by_month[month][5] for month in months],
                "borderColor": "#2ECC71"
            },
            {
                "label": "4 звезды",
                "data": [ratings_count_by_month[month][4] for month in months],
                "borderColor": "#3498DB"
            },
            {
                "label": "3 звезды",
                "data": [ratings_count_by_month[month][3] for month in months],
                "borderColor": "#9B59B6"
            },
            {
                "label": "2 звезды",
                "data": [ratings_count_by_month[month][2] for month in months],
                "borderColor": "#F1C40F"
            },
            {
                "label": "1 звезда",
                "data": [ratings_count_by_month[month][1] for month in months],
                "borderColor": "#E74C3C"
            }
        ]
    }

    return jsonify({
        "success": True,
        "data": data,
        "message": "Данные по ratings-trend получены"
    }), 200

# "labels": ["★☆☆☆☆", "★★☆☆☆", "★★★☆☆", "★★★★☆", "★★★★★"]
