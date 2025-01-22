import json
from flask import Flask, Response
from sqlalchemy.orm import sessionmaker
from data_base.data_main import YandexReview, engine

# Создаём приложение Flask
app = Flask(__name__)

# Настройка сессии для работы с базой данных
Session = sessionmaker(bind=engine)
session = Session()


@app.route('/api/first-yandex-author', methods=['GET'])
def get_first_yandex_author():
    # Запрос для получения первого автора из таблицы YandexReview
    first_review = session.query(YandexReview).first()

    if first_review:
        # Сериализация с ensure_ascii=False
        data = json.dumps({
            "success": True,
            "author": first_review.author
        }, ensure_ascii=False)
        return Response(data, mimetype='application/json')
    else:
        data = json.dumps({
            "success": False,
            "message": "No reviews found"
        }, ensure_ascii=False)
        return Response(data, mimetype='application/json')
