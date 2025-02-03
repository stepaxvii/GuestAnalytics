import logging

from datetime import datetime
from dateutil.relativedelta import relativedelta

from flask import Blueprint, jsonify, request

from data_base.data_main import YandexReview, session
from data_base.read_data import read_rest_ya_reviews
from utils.date import month_dict

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)


sentiment_distribution_bp = Blueprint('sentiment_distribution', __name__)


@sentiment_distribution_bp.route('/sentiment-distribution', methods=['GET'])
def sentiment_distribution():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан user_id"
        }), 400

    data = {
        "labels": ["Положительные", "Нейтральные", "Отрицательные"],
        "values": [70, 20, 10]
    }

    return jsonify({
        "success": True,
        "data": data,
        "message": "Данные по sentiment-distribution получены"
    }), 200


sentiment_trend_bp = Blueprint('sentiment_trend', __name__)


# @sentiment_trend_bp.route('/sentiment-trend', methods=['GET'])
# def sentiment_trend():
#     # Получаем user_id, который совпадает с restaurant_id
#     user_id = request.args.get('user_id')
#     if not user_id:
#         return jsonify({
#             "success": False,
#             "data": None,
#             "message": "Не указан user_id"
#         }), 400

#     # Пример запроса, чтобы получить отзывы по restaurant_id (user_id)
#     reviews = session.query(YandexReview).filter(
#         YandexReview.restaurant_id == user_id
#     ).all()

#     # Если нет отзывов, возвращаем пустой ответ
#     if not reviews:
#         return jsonify({
#             "success": False,
#             "data": None,
#             "message": "Отзывы не найдены"
#         }), 404

#     # Получаем текущую дату
#     current_date = datetime.now()

#     # Генерируем список последних 4 месяцев в формате 'yyyy-mm'
#     months = []
#     for i in range(3, -1, -1):  # Сначала добавляем старые месяцы, начиная с 3
#         prev_month_date = current_date - relativedelta(months=i)
#         prev_month = prev_month_date.strftime("%Y-%m")
#         months.append(prev_month)

#     # Создаем словарь для подсчета количества отзывов по каждому настроению для каждого месяца
#     sentiment_counts = {
#         "positive": {month: 0 for month in months},
#         "neutral": {month: 0 for month in months},
#         "negative": {month: 0 for month in months}
#     }

#     # Перебираем все отзывы и распределяем по месяцам и настроению
#     for review in reviews:
#         # Преобразуем строку в datetime (формат даты 'YYYY-MM-DD')
#         review_date = datetime.strptime(review.created_at, "%Y-%m-%d")

#         # Получаем месяц и год отзыва в формате 'yyyy-mm'
#         review_month = review_date.strftime("%Y-%m")

#         # Если месяц отзыва есть в нашем списке, увеличиваем соответствующий счетчик
#         if review_month in months:
#             if review.semantic == "П":  # Положительные отзывы
#                 sentiment_counts["positive"][review_month] += 1
#             elif review.semantic == "Н":  # Нейтральные отзывы
#                 sentiment_counts["neutral"][review_month] += 1
#             elif review.semantic == "О":  # Отрицательные отзывы
#                 sentiment_counts["negative"][review_month] += 1

#     # Формируем данные для графика
#     data = {
#         "labels": ["Январь", "Февраль", "Март", "Апрель"],
#         "datasets": [
#             {
#                 "label": "Положительные",
#                 "data": [sentiment_counts["positive"][month] for month in months],
#                 "borderColor": "#2ECC71"
#             },
#             {
#                 "label": "Нейтральные",
#                 "data": [sentiment_counts["neutral"][month] for month in months],
#                 "borderColor": "#1E90FF"
#             },
#             {
#                 "label": "Отрицательные",
#                 "data": [sentiment_counts["negative"][month] for month in months],
#                 "borderColor": "#FF6347"
#             }
#         ]
#     }

#     return jsonify({
#         "success": True,
#         "data": data,
#         "message": "Данные по sentiment-trend получены"
#     }), 200

@sentiment_trend_bp.route('/sentiment-trend', methods=['GET'])
def sentiment_trend():
    # Получаем user_id, который совпадает с restaurant_id
    user_id = request.args.get('user_id')
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

    # Генерируем список последних 4 месяцев в формате 'yyyy-mm'
    months = []
    for i in range(3, -1, -1):  # Сначала добавляем старые месяцы, начиная с 3
        prev_month_date = current_date - relativedelta(months=i)
        prev_month = prev_month_date.strftime("%Y-%m")
        months.append(prev_month)

    # Создаем словарь для подсчета количества отзывов по каждому настроению для каждого месяца
    sentiment_counts = {
        "positive": {month: 0 for month in months},
        "neutral": {month: 0 for month in months},
        "negative": {month: 0 for month in months}
    }

    # Перебираем все отзывы и распределяем по месяцам и настроению
    for review in reviews:
        # Преобразуем строку в datetime (формат даты 'YYYY-MM-DD')
        review_date = datetime.strptime(review.created_at, "%Y-%m-%d")

        # Получаем месяц и год отзыва в формате 'yyyy-mm'
        review_month = review_date.strftime("%Y-%m")

        # Если месяц отзыва есть в нашем списке, увеличиваем соответствующий счетчик
        if review_month in months:
            if review.semantic == "П":  # Положительные отзывы
                sentiment_counts["positive"][review_month] += 1
            elif review.semantic == "Н":  # Нейтральные отзывы
                sentiment_counts["neutral"][review_month] += 1
            elif review.semantic == "О":  # Отрицательные отзывы
                sentiment_counts["negative"][review_month] += 1

    # Преобразуем месяцы в названия на русском с использованием month_dict
    months_labels = [month_dict[month.split('-')[1]] for month in months]

    # Формируем данные для графика
    data = {
        "labels": months_labels,  # Теперь в labels будут русские названия месяцев
        "datasets": [
            {
                "label": "Положительные",
                "data": [sentiment_counts["positive"][month] for month in months],
                "borderColor": "#2ECC71"
            },
            {
                "label": "Нейтральные",
                "data": [sentiment_counts["neutral"][month] for month in months],
                "borderColor": "#1E90FF"
            },
            {
                "label": "Отрицательные",
                "data": [sentiment_counts["negative"][month] for month in months],
                "borderColor": "#FF6347"
            }
        ]
    }

    return jsonify({
        "success": True,
        "data": data,
        "message": "Данные по sentiment-trend получены"
    }), 200
