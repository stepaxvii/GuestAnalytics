import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import Blueprint, jsonify, request

from data.read_data import read_rest_ya_reviews
from utils.date import month_dict

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)

sentiment_distribution_bp = Blueprint('sentiment_distribution', __name__)


@sentiment_distribution_bp.route('/sentiment-distribution', methods=['GET'])
def sentiment_distribution():
    restaurant_id = request.args.get('restaurant_id')
    if not restaurant_id:
        logging.error('Не указан restaurant_id')
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан restaurant_id"
        }), 400

    try:
        # Получаем все отзывы для данного ресторана
        reviews = read_rest_ya_reviews(restaurant_id=restaurant_id)

        # Если нет отзывов, возвращаем пустой ответ
        if not reviews:
            logging.warning(
                f"Отзывы не найдены для restaurant_id {restaurant_id}"
            )
            return jsonify({
                "success": False,
                "data": None,
                "message": "Отзывы не найдены"
            }), 404

        # Получаем текущий месяц
        current_date = datetime.now()
        current_month = current_date.strftime("%Y-%m")

        # Фильтруем отзывы за текущий месяц
        current_month_reviews = [
            review for review in reviews if review.created_at.startswith(
                current_month
            )
        ]

        # Считаем количество каждого типа настроения
        sentiment_counts = {
            "positive": 0,
            "neutral": 0,
            "negative": 0
        }

        for review in current_month_reviews:
            # Приводим к верхнему регистру и
            # проверяем наличие нужной оценки в строке
            semantic = review.semantic.upper()
            if "П" in semantic:
                sentiment_counts["positive"] += 1
            elif "Н" in semantic:
                sentiment_counts["neutral"] += 1
            elif "О" in semantic:
                sentiment_counts["negative"] += 1

        # Формируем данные для графика
        data = {
            "labels": ["Положительные", "Нейтральные", "Отрицательные"],
            "values": [
                sentiment_counts["positive"],
                sentiment_counts["neutral"],
                sentiment_counts["negative"]
            ]
        }

        logging.info(f"Данные для restaurant_id {restaurant_id} получены")
        return jsonify({
            "success": True,
            "data": data,
            "message": "Данные по sentiment-distribution получены"
        }), 200
    except Exception as e:
        logging.error(f"Ошибка при обработке запроса: {e}")
        return jsonify({
            "success": False,
            "data": None,
            "message": "Произошла ошибка"
        }), 500


sentiment_trend_bp = Blueprint('sentiment_trend', __name__)


@sentiment_trend_bp.route('/sentiment-trend', methods=['GET'])
def sentiment_trend():
    restaurant_id = request.args.get('restaurant_id')
    if not restaurant_id:
        logging.error('Не указан restaurant_id')
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан restaurant_id"
        }), 400

    try:
        # Пример запроса, чтобы получить отзывы по restaurant_id
        reviews = read_rest_ya_reviews(restaurant_id=restaurant_id)

        # Если нет отзывов, возвращаем пустой ответ
        if not reviews:
            logging.warning(
                f"Отзывы не найдены для restaurant_id {restaurant_id}"
            )
            return jsonify({
                "success": False,
                "data": None,
                "message": "Отзывы не найдены"
            }), 404

        # Получаем текущую дату
        current_date = datetime.now()

        # Генерируем список последних 4 месяцев в формате 'yyyy-mm'
        months = []
        for i in range(3, -1, -1):  # Начинаем с самого старого месяца
            prev_month_date = current_date - relativedelta(months=i)
            prev_month = prev_month_date.strftime("%Y-%m")
            months.append(prev_month)

        # Создаем словарь для подсчета количества отзывов по каждому настроению
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

            # Если месяц отзыва есть в нашем списке, увеличиваем счетчик
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
            "labels": months_labels,
            "datasets": [
                {
                    "label": "Положительные",
                    "data": [
                        sentiment_counts["positive"][month] for month in months
                    ],
                    "borderColor": "#2ECC71"
                },
                {
                    "label": "Нейтральные",
                    "data": [
                        sentiment_counts["neutral"][month] for month in months
                    ],
                    "borderColor": "#1E90FF"
                },
                {
                    "label": "Отрицательные",
                    "data": [
                        sentiment_counts["negative"][month] for month in months
                    ],
                    "borderColor": "#FF6347"
                }
            ]
        }

        logging.info(f"Данные для restaurant_id {restaurant_id} получены")
        return jsonify({
            "success": True,
            "data": data,
            "message": "Данные по sentiment-trend получены"
        }), 200
    except Exception as e:
        logging.error(f"Ошибка при обработке запроса: {e}")
        return jsonify({
            "success": False,
            "data": None,
            "message": "Произошла ошибка"
        }), 500
