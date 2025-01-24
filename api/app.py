import logging

from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from data_base.data_main import YandexReview, engine
import urllib.parse

# Создаём приложение Flask
app = Flask(__name__)

# Разрешаем CORS для всех источников
CORS(app)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


@app.route('/api/total-reviews', methods=['GET'])
def get_total_reviews():
    # Получаем cookie с данными о пользователе
    cookie = request.cookies.get(
        'wordpress_logged_in_d5be2c11d7a17c96d47fd4cfeb45020a'
    )
    if cookie:
        # Декодируем URL-кодирование в cookie
        decoded_cookie = urllib.parse.unquote(cookie)

        # Разделяем cookie по символу '|'
        cookie_parts = decoded_cookie.split('|')

        # Проверяем, что структура cookie правильная
        if len(cookie_parts) >= 2:
            nickname = cookie_parts[0]

            # Выводим в лог никнейм и ID для отладки
            logger.info(f"Nickname: {nickname}")

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
        return jsonify({"success": False, "message": "Not identified"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
