from datetime import datetime
from dateutil.relativedelta import relativedelta

from flask import Blueprint, jsonify, request

from data_base.data_main import YandexReview, session
from utils.date import month_dict

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
#     user_id = request.args.get('user_id')
#     if not user_id:
#         return jsonify({
#             "success": False,
#             "data": None,
#             "message": "Не указан user_id"
#         }), 400

#     data = {
#         "labels": ["Январь", "Февраль", "Март", "Апрель"],
#         "datasets": [
#             {
#                 "label": "Положительные",
#                 "data": [50, 60, 55, 70],
#                 "borderColor": "#2ECC71"
#             },
#             {
#                 "label": "Нейтральные",
#                 "data": [30, 25, 30, 20],
#                 "borderColor": "#1E90FF"
#             },
#             {
#                 "label": "Отрицательные",
#                 "data": [20, 15, 15, 10],
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

    # Получаем текущую дату
    current_date = datetime.now()

    # Генерируем список последних 4 месяцев в формате 'yyyy-mm'
    months = []
    for i in range(3, -1, -1):  # Сначала добавляем старые месяцы, начиная с 3
        # Используем relativedelta для точного вычитания месяцев
        prev_month_date = current_date - relativedelta(months=i)
        # Форматируем как 'yyyy-mm'
        prev_month = prev_month_date.strftime("%Y-%m")
        months.append(prev_month)

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

    # Создаем словарь для хранения количества  отзывов по месяцам
    sentiment_data = {
        "П": {month: 0 for month in months},
        "Н": {month: 0 for month in months},
        "О": {month: 0 for month in months}
    }

    # Функция для очистки и обработки значения поля semantic
    def get_sentiment(semantic_value):
        # Приводим к верхнему регистру и фильтруем только разрешенные символы
        clean_value = ''.join(
            [ch.upper() for ch in str(semantic_value) if ch.isalpha()]
        )

        # Если символ является 'О', 'Н' или 'П'
        if clean_value == 'П':
            return "П"
        elif clean_value == 'Н':
            return "Н"
        elif clean_value == 'О':
            return "О"
        # Для всех других случаев, считаем нейтральным
        else:
            return "Н"

    # Перебираем все отзывы
    for review in reviews:
        # Преобразуем строку в datetime (формат даты 'YYYY-MM-DD')
        review_date = datetime.strptime(review.created_at, "%Y-%m-%d")

        # Получаем месяц и год отзыва в формате 'yyyy-mm'
        review_month = review_date.strftime("%Y-%m")

        # Если месяц отзыва есть в нашем списке, считаем его для sentiment
        if review_month in sentiment_data:
            # Применяем функцию очистки и обработки
            sentiment = get_sentiment(review.semantic)

            # Увеличиваем соответствующий счетчик
            sentiment_data[sentiment][review_month] += 1

    # Переходим к подготовке данных для графика
    data = {
        "labels": [month_dict[month.split('-')[1]] for month in months],
        "datasets": [
            {
                "label": "Положительные",
                "data": [
                    sentiment_data["П"].get(month, 0) for month in months
                ],
                "borderColor": "#2ECC71"
            },
            {
                "label": "Нейтральные",
                "data": [
                    sentiment_data["Н"].get(month, 0) for month in months
                ],
                "borderColor": "#1E90FF"
            },
            {
                "label": "Отрицательные",
                "data": [
                    sentiment_data["О"].get(month, 0) for month in months
                ],
                "borderColor": "#FF6347"
            }
        ]
    }

    return jsonify({
        "success": True,
        "data": data,
        "message": "Данные по sentiment-trend получены"
    }), 200
