# from flask import Flask, render_template
# import plotly.express as px
# import plotly.io as pio

# # Создаём приложение Flask
# app = Flask(__name__)


# @app.route('/')
# def index():
#     # Данные для диаграммы
#     data = {
#         'Месяц': ['Январь', 'Февраль', 'Март', 'Апрель', 'Май'],
#         'Продажи': [12, 19, 3, 5, 2]
#     }

#     # Создаем диаграмму с использованием Plotly
#     fig = px.bar(data, x='Месяц', y='Продажи', title='Продажи за месяц')

#     # Преобразуем диаграмму в HTML
#     graph_html = pio.to_html(fig, full_html=False)

#     return render_template('index.html', graph_html=graph_html)


# if __name__ == '__main__':
#     app.run(debug=True)


# from sqlalchemy import func, create_engine
# from sqlalchemy.orm import declarative_base, sessionmaker
# from datetime import datetime

# from data_base.data_main import YandexReview

# # Настраиваем базу данных
# DATA_URL = "sqlite:///guestanal.db"
# Base = declarative_base()
# engine = create_engine(DATA_URL)
# Session = sessionmaker(bind=engine)

# Session()
# session = Session()
# # Фильтруем отзывы по дате и группируем их по месяцам
# reviews_per_month = session.query(
#     func.extract('month', YandexReview.created_at).label('month'),  # Извлекаем месяц из даты
#     func.count(YandexReview.id).label('reviews_count')  # Подсчитываем количество отзывов
# ).filter(
#     # Фильтруем только отзывы за октябрь, ноябрь и декабрь 2024 года (или любой другой год)
#     YandexReview.restaurant_id == 4,
#     func.extract('year', YandexReview.created_at) == 2024,
#     func.extract('month', YandexReview.created_at).in_([9, 10, 11, 12])
# ).group_by(
#     'month'
# ).all()

# # Выводим данные для проверки
# for month, count in reviews_per_month:
#     print(f"Month: {month}, Reviews count: {count}")


# import plotly.express as px

# # Разбиваем данные по месяцам и количеству отзывов
# months = ['Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
# review_counts = [count for _, count in reviews_per_month]

# # Создаем DataFrame (если нужно, можно использовать pandas)
# import pandas as pd
# data = pd.DataFrame({
#     'Month': months,
#     'Reviews Count': review_counts
# })

# # Строим диаграмму
# fig = px.bar(data, x='Month', y='Reviews Count', title='Количество отзывов по месяцам 2024')

# # Отображаем диаграмму
# fig.show()


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

    # Проверяем количество полученных данных и формируем ответ
    review_counts = {}
    for i, (month, count) in enumerate(reviews_per_month):
        if month >= 9 and month <= 12:  # Ограничиваем по месяцам с 9 по 12
            review_counts[months[month - 9]] = count

    # Возвращаем данные в формате JSON
    return jsonify({
        "success": True,
        "data": review_counts
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
