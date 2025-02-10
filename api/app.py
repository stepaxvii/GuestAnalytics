# api/app.py
from flask import Flask
from api.charts import (
    ratings,
    reviews,
    sentiment
)
from api.restaurants import create_restaurant
from api.reviews import check_reviews
from api.db import create_tables  # Импортируем функцию для создания таблиц

app = Flask(__name__)

# Создаем таблицы, если их еще нет
create_tables()

# Регистрируем Blueprint для каждого API
app.register_blueprint(reviews.total_reviews_bp, url_prefix='/api')
app.register_blueprint(reviews.trend_reviews_bp, url_prefix='/api')
app.register_blueprint(ratings.ratings_distribution_bp, url_prefix='/api')
app.register_blueprint(ratings.ratings_trend_bp, url_prefix='/api')
app.register_blueprint(sentiment.sentiment_distribution_bp, url_prefix='/api')
app.register_blueprint(sentiment.sentiment_trend_bp, url_prefix='/api')
app.register_blueprint(check_reviews.yandex_coll_bp, url_prefix='/api')
app.register_blueprint(
    create_restaurant.create_restaurant_bp, url_prefix='/api'
)
app.register_blueprint(
    check_reviews.yandex_prim_coll_bp, url_prefix='/api'
)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
