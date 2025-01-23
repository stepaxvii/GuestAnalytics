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
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from data_base.data_main import YandexReview, engine

# Создаём приложение Flask
app = Flask(__name__)

# Настройка сессии для работы с базой данных
Session = sessionmaker(bind=engine)
session = Session()


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


@app.route('/api/total-reviews', methods=['GET'])
def get_total_reviews():
    # Извлекаем никнейм пользователя из cookie
    cookies = request.cookies.get('wordpress_logged_in_')

    # Проверим, если cookie существует
    if cookies:
        # Разделим строку cookie, чтобы получить никнейм (предполагаем, что структура 'Имя|ID|...'):
        try:
            nickname = cookies.split('|')[0]  # Получаем никнейм (первая часть)
        except IndexError:
            return jsonify({"error": "Invalid cookie format"}), 400

        # Теперь в зависимости от никнейма возвращаем разные данные
        if nickname == 'Igor':
            return jsonify({
                "success": True,
                "data": {
                    "total_reviews": 200,
                    "percentage_change": 5.0
                }
            })
        elif nickname == 'Maksym':
            return jsonify({
                "success": True,
                "data": {
                    "total_reviews": 150,
                    "percentage_change": 3.5
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
        return jsonify({"success": False, "message": "User not identified"}), 400


@app.route('/api/', methods=['GET'])
def get_1():
    pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
