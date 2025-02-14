from flask import Blueprint, jsonify, request
from datetime import datetime
from dateutil.relativedelta import relativedelta

from api.db import session
from data.data_main import YandexReview
from utils.date import month_dict

trend_reviews_bp = Blueprint('trend_reviews', __name__)


@trend_reviews_bp.route('/trend-reviews', methods=['GET'])
def trend_reviews():
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
        # Используем relativedelta для точного вычитания месяцев
        prev_month_date = current_date - relativedelta(months=i)
        # Форматируем как 'yyyy-mm'
        prev_month = prev_month_date.strftime("%Y-%m")
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

    # Теперь преобразуем ключи в месяц и год в название месяца
    months_labels = [
        month_dict[month.split('-')[1]] for month in months_data.keys()
    ]

    # Переходим к подготовке данных для графика
    data = {
        "labels": months_labels,  # Теперь в labels будут названия месяцев
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
    user_id = request.args.get('user_id')

    # Проверка, что user_id был передан
    if not user_id:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан user_id"
        }), 400

    # # Проверка, что user_id можно преобразовать в целое число
    # try:
    #     user_id = int(user_id_str)
    # except ValueError:
    #     return jsonify({
    #         "success": False,
    #         "data": None,
    #         "message": "Некорректный user_id"
    #     }), 400

    # Получаем текущую дату
    current_date = datetime.now()

    # Получаем текущий год и месяц в формате 'yyyy-mm'
    current_month = current_date.strftime("%Y-%m")

    # Получаем предыдущий месяц
    prev_month_date = current_date - relativedelta(months=1)
    prev_month = prev_month_date.strftime("%Y-%m")

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

    # Подсчитываем количество отзывов для текущего месяца
    total_reviews_this_month = session.query(YandexReview).filter(
        YandexReview.restaurant_id == user_id,
        YandexReview.created_at.like(f"{current_month}%")
    ).count()

    # Подсчитываем количество отзывов для предыдущего месяца
    total_reviews_prev_month = session.query(YandexReview).filter(
        YandexReview.restaurant_id == user_id,
        YandexReview.created_at.like(f"{prev_month}%")
    ).count()

    # Вычисляем процентное изменение (если предыдущий месяц не ноль)
    if total_reviews_prev_month > 0:
        percentage_change = (
            (
                total_reviews_this_month - total_reviews_prev_month
            ) / total_reviews_prev_month
        ) * 100
        # Округляем процентное изменение до одного знака после запятой
        percentage_change = round(percentage_change, 1)
    else:
        percentage_change = 100

    return jsonify({
        "success": True,
        "data": {
            "total_reviews": total_reviews_this_month,
            "percentage_change": percentage_change
        },
        "message": "Данные по total-reviews получены"
    }), 200
