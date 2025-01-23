# from flask import Flask, jsonify
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import func
# from data_base.data_main import YandexReview, engine

# # Создаём приложение Flask
# app = Flask(__name__)

# # Настройка сессии для работы с базой данных
# Session = sessionmaker(bind=engine)
# session = Session()


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
#         "data": review_counts
#     })


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)


from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from data_base.data_main import YandexReview, engine
import urllib.parse

# Создаём приложение Flask
app = Flask(__name__)

CORS(app)  # Разрешаем CORS для всех источников

# Настройка сессии для работы с базой данных
Session = sessionmaker(bind=engine)
session = Session()

# Включение отладки
app.config['DEBUG'] = True


@app.route('/api/yandex-reviews-by-month', methods=['GET'])
def get_reviews_by_month():
    # Фильтруем отзывы по дате и группируем их по месяцам
    reviews_per_month = session.query(
        func.extract('month', YandexReview.created_at).label('month'),
        func.count(YandexReview.id).label('reviews_count')
    ).filter(
        YandexReview.restaurant_id == 4,  # Пример restaurant_id
        func.extract('year', YandexReview.created_at) == 2024,
        func.extract('month', YandexReview.created_at).in_([9, 10, 11, 12])
    ).group_by(
        'month'
    ).all()

    # Месяцы для отображения
    months = ['Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

    # Проверяем количество полученных данных и формируем ответ
    review_counts = {}
    for i, (month, count) in enumerate(reviews_per_month):
        if month >= 9 and month <= 12:  # Ограничиваем по месяцам с 9 по 12
            review_counts[months[month - 9]] = count

    # Возвращаем данные в формате JSON
    return jsonify({
        "success": True,
        "data": {
            "гавно": 2,
            "дрочь": 8,
            "успех": 70
        }
    })


# @app.route('/api/total-reviews', methods=['GET'])
# def get_total_reviews():

#     # Отправляем количество отзывов
#     return jsonify({
#         "success": True,
#         "data": {
#             "total_reviews": 126,
#             "percentage_change": 4.75
#         }
#     })
# @app.route('/api/total-reviews', methods=['GET'])
# def get_total_reviews():
#     # Печать всех cookies
#     print("Received cookies:", request.cookies)

#     # Извлекаем cookie с именем пользователя
#     cookie = request.cookies.get('wordpress_logged_in_d5be2c11d7a17c96d47fd4cfeb45020a')
#     if cookie:
#         # Декодируем URL-кодирование в cookie
#         decoded_cookie = urllib.parse.unquote(cookie)  # Декодируем %7C в |

#         # Разделяем cookie по символу '|'
#         cookie_parts = decoded_cookie.split('|')

#         # Проверяем, что структура cookie правильная
#         if len(cookie_parts) >= 2:
#             nickname = cookie_parts[0]  # Первая часть — это никнейм пользователя
#             user_id = cookie_parts[1]  # Вторая часть — это ID пользователя

#             # Логика ответа
#             if nickname == 'Igor':
#                 return jsonify({
#                     "success": True,
#                     "data": {
#                         "total_reviews": 200,
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
#         return jsonify({"success": False, "message": "User not identified"}), 400


# @app.route('/api/total-reviews', methods=['GET'])
# def get_total_reviews():
#     # Получаем все cookies
#     print("Received cookies:", request.cookies)

#     user_cookie = request.cookies.get('wordpress_logged_in_d5be2c11d7a17c96d47fd4cfeb45020a')
#     if user_cookie:
#         print(f"User identified: {user_cookie}")
#         return jsonify({"success": True, "message": "User identified"})
#     else:
#         print("User not identified")
#         return jsonify({"success": False, "message": "User not identified"}), 400


@app.route('/api/total-reviews', methods=['GET'])
def get_total_reviews():
    # Печатаем все данные запроса
    print("Request Headers:")
    print(request.headers)

    print("Request Cookies:")
    print(request.cookies)

    print("Request Args (Query Params):")
    print(request.args)

    print("Request Form Data:")
    print(request.form)

    print("Request Data (Raw Body Data):")
    print(request.data)

    # Получаем cookie с данными о пользователе
    cookie = request.cookies.get('wordpress_logged_in_d5be2c11d7a17c96d47fd4cfeb45020a')
    if cookie:
        # Декодируем URL-кодирование в cookie
        decoded_cookie = urllib.parse.unquote(cookie)

        # Разделяем cookie по символу '|'
        cookie_parts = decoded_cookie.split('|')

        # Проверяем, что структура cookie правильная
        if len(cookie_parts) >= 2:
            nickname = cookie_parts[0]  # Первая часть — это никнейм пользователя
            user_id = cookie_parts[1]  # Вторая часть — это ID пользователя

            # Выводим в лог никнейм и ID для отладки
            print(f"Nickname: {nickname}, User ID: {user_id}")

            # Логика ответа в зависимости от никнейма
            if nickname == 'Igor':
                return jsonify({
                    "success": True,
                    "data": {
                        "total_reviews": 200,
                        "percentage_change": 5.0
                    }
                })
            if nickname == 'Maksym':
                return jsonify({
                    "success": True,
                    "data": {
                        "total_reviews": 700,
                        "percentage_change": 5.0
                    }
                })
            else:
                return jsonify({
                    "success": True,
                    "data": {
                        "total_reviews": 126,
                        "percentage_change": 4.75
                    }
                })
        else:
            return jsonify({"error": "Invalid cookie format"}), 400
    else:
        return jsonify({"success": False, "message": "User not identified"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
