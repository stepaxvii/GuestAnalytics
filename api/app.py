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


from flask import Flask, jsonify
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

    # Подсчёт общего количества отзывов
    total_reviews = sum(count for _, count in reviews_per_month)

    # Проверяем количество полученных данных и формируем ответ
    review_counts = {}
    for i, (month, count) in enumerate(reviews_per_month):
        if month >= 9 and month <= 12:  # Ограничиваем по месяцам с 9 по 12
            review_counts[months[month - 9]] = count

    # Формируем данные для графика с процентами
    percentages = [count / total_reviews * 100 if total_reviews > 0 else 0 for count in review_counts.values()]

    # Возвращаем данные в формате JSON
    return jsonify({
        "success": True,
        "data": {
            "counts": review_counts,
            "percentages": percentages,
            "total": total_reviews
        }
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
