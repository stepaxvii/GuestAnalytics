# import logging

# from flask import Flask, jsonify, request
# from flask_cors import CORS
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import func
# from data_base.data_main import YandexReview, engine
# import urllib.parse

# # Создаём приложение Flask
# app = Flask(__name__)

# # Разрешаем CORS для всех источников
# CORS(app)

# # Настройка логирования
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Настройка сессии для работы с базой данных
# Session = sessionmaker(bind=engine)
# session = Session()

# # Включение отладки
# app.config['DEBUG'] = True


# @app.route('/api/yandex-reviews-by-month', methods=['GET'])
# def get_reviews_by_month():
#     # Фильтруем отзывы по дате и группируем их по месяцам
#     reviews_per_month = session.query(
#         func.extract('month', YandexReview.created_at).label('month'),
#         func.count(YandexReview.id).label('reviews_count')
#     ).filter(
#         YandexReview.restaurant_id == 4,  # Пример restaurant_id
#         func.extract('year', YandexReview.created_at) == 2024,
#         func.extract('month', YandexReview.created_at).in_([9, 10, 11, 12])
#     ).group_by(
#         'month'
#     ).all()

#     # Месяцы для отображения
#     months = ['Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

#     # Проверяем количество полученных данных и формируем ответ
#     review_counts = {}
#     for i, (month, count) in enumerate(reviews_per_month):
#         if month >= 9 and month <= 12:  # Ограничиваем по месяцам с 9 по 12
#             review_counts[months[month - 9]] = count

#     # Возвращаем данные в формате JSON
#     return jsonify({
#         "success": True,
#         "data": {
#             "гавно": 2,
#             "дрочь": 8,
#             "успех": 70
#         }
#     })


# @app.route('/api/total-reviews', methods=['GET'])
# def get_total_reviews():
#     # Получаем cookie с данными о пользователе
#     cookie = request.cookies.get(
#         'wordpress_logged_in_d5be2c11d7a17c96d47fd4cfeb45020a'
#     )
#     if cookie:
#         # Декодируем URL-кодирование в cookie
#         decoded_cookie = urllib.parse.unquote(cookie)

#         # Разделяем cookie по символу '|'
#         cookie_parts = decoded_cookie.split('|')

#         # Проверяем, что структура cookie правильная
#         if len(cookie_parts) >= 2:
#             nickname = cookie_parts[0]

#             # Выводим в лог никнейм и ID для отладки
#             logger.info(f"Nickname: {nickname}")

#             # Логика ответа в зависимости от никнейма
#             if nickname == 'Igor':
#                 return jsonify({
#                     "success": True,
#                     "data": {
#                         "total_reviews": 200,
#                         "percentage_change": 5.0
#                     }
#                 })
#             if nickname == 'Maksym':
#                 return jsonify({
#                     "success": True,
#                     "data": {
#                         "total_reviews": 700,
#                         "percentage_change": 5.0
#                     }
#                 })
#             else:
#                 return jsonify({
#                     "success": True,
#                     "data": {
#                         "total_reviews": 126,
#                         "percentage_change": 4.75
#                     }
#                 })
#         else:
#             return jsonify({"error": "Invalid cookie format"}), 400
#     else:
#         return jsonify({"success": False, "message": "Not identified"}), 400


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)


from flask import Flask, jsonify, request

app = Flask(__name__)


# 1) /api/total-reviews
@app.route('/api/total-reviews', methods=['GET'])
def total_reviews():
    user_id = int(request.args.get('user_id'))
    print(f"------{user_id}----------")
    if not user_id:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан user_id"
        }), 400

    if user_id == 1:

        total_reviews = 234
        percentage_change = 100.2  # Условно +10.2%

    if user_id == 2:

        total_reviews = 432
        percentage_change = 30.2  # Условно +10.2%

    return jsonify({
        "success": True,
        "data": {
            "total_reviews": total_reviews,
            "percentage_change": percentage_change
        },
        "message": "Данные по total-reviews получены"
    }), 200


# 2) /api/trend-reviews
@app.route('/api/trend-reviews', methods=['GET'])
def trend_reviews():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан user_id"
        }), 400

    # Пример данных
    data = {
        "labels": ["Январь", "Февраль", "Март", "Апрель"],
        "dataset": {
            "label": "Отзывы",
            "data": [100, 120, 140, 160],
            "borderColor": "#36A2EB"
        }
    }

    return jsonify({
        "success": True,
        "data": data,
        "message": "Данные по trend-reviews получены"
    }), 200


# 3) /api/ratings-distribution
@app.route('/api/ratings-distribution', methods=['GET'])
def ratings_distribution():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан user_id"
        }), 400

    # Пример данных
    data = {
        "labels": ["5 звёзд", "4 звезды", "3 звезды", "2 звезды", "1 звезда"],
        "values": [50, 30, 10, 5, 5]
    }

    return jsonify({
        "success": True,
        "data": data,
        "message": "Данные по ratings-distribution получены"
    }), 200


# 4) /api/ratings-trend
@app.route('/api/ratings-trend', methods=['GET'])
def ratings_trend():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан user_id"
        }), 400

    # Пример данных: несколько серий (5 звёзд, 4 звёзды и т.п.)
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


# 5) /api/sentiment-distribution
@app.route('/api/sentiment-distribution', methods=['GET'])
def sentiment_distribution():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан user_id"
        }), 400

    # Пример данных
    data = {
        "labels": ["Положительные", "Нейтральные", "Отрицательные"],
        "values": [70, 20, 10]
    }

    return jsonify({
        "success": True,
        "data": data,
        "message": "Данные по sentiment-distribution получены"
    }), 200


# 6) /api/sentiment-trend
@app.route('/api/sentiment-trend', methods=['GET'])
def sentiment_trend():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан user_id"
        }), 400

    # Пример данных: 3 линии — Положительные, Нейтральные, Отрицательные
    data = {
        "labels": ["Январь", "Февраль", "Март", "Апрель"],
        "datasets": [
            {
                "label": "Положительные",
                "data": [50, 60, 55, 70],
                "borderColor": "#2ECC71"
            },
            {
                "label": "Нейтральные",
                "data": [30, 25, 30, 20],
                "borderColor": "#1E90FF"
            },
            {
                "label": "Отрицательные",
                "data": [20, 15, 15, 10],
                "borderColor": "#FF6347"
            }
        ]
    }

    return jsonify({
        "success": True,
        "data": data,
        "message": "Данные по sentiment-trend получены"
    }), 200


# -- Запуск приложения --
if __name__ == '__main__':
    # Запуск на порту 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
