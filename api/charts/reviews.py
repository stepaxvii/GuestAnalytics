from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta

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

    # Получаем текущую дату
    # current_month = datetime.now().month
    # current_year = datetime.now().year

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
    
    # Получаем список месяцев за последние 4 месяца, включая текущий
    months_data = {}
    for i in range(4):
        # Для каждого месяца получаем дату в прошлом
        month_date = current_date - timedelta(days=i * 30)
        month_name = month_date.strftime("%B")  # Получаем название месяца
        months_data[month_name] = 0  # Инициализируем месяц с нулевой суммой рейтинга

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
    
    # Перебираем все отзывы
    for review in reviews:
        # Преобразуем строку в datetime (формат даты 'YYYY-MM-DD')
        review_date = datetime.strptime(review.created_at, "%Y-%m-%d")
        
        # Получаем месяц и год отзыва
        month_name = review_date.strftime("%B")  # Получаем название месяца
        
        # Если месяц находится в последние 4 месяца, то добавляем рейтинг
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
    # # Данные для графика (по месяцам)
    # months_data = {"Январь": 0, "Февраль": 0, "Март": 0, "Апрель": 0}
    
    # # Перебираем все отзывы
    # for review in reviews:
    #     # Преобразуем строку в datetime (формат даты 'YYYY-MM-DD')
    #     review_date = datetime.strptime(review.created_at, "%Y-%m-%d")
        
    #     # Получаем месяц в числовом формате (1-12)
    #     month_num = review_date.month
        
    #     # Сопоставляем числовой месяц с названием месяца
    #     month_names = {
    #         1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
    #         5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
    #         9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
    #     }
        
    #     month_name = month_names.get(month_num)
        
    #     # Если месяц входит в наш диапазон (например, Январь - Апрель), то добавляем рейтинг
    #     if month_name in months_data:
    #         months_data[month_name] += review.rating  # Суммируем рейтинг для каждого месяца

    # # Переходим к подготовке данных для графика
    # data = {
    #     "labels": list(months_data.keys()),
    #     "dataset": {
    #         "label": "Отзывы",
    #         "data": list(months_data.values()),
    #         "borderColor": "#36A2EB"
    #     }
    # }

    # return jsonify({
    #     "success": True,
    #     "data": data,
    #     "message": "Данные по trend-reviews получены"
    # }), 200

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
