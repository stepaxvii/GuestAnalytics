import logging

from flask import Flask
from api.charts import (
    dashboard,
    ratings,
    reviews,
    sentiment
)
from api.restaurants import (
    change_subscription,
    create_restaurant,
    edit_restaurant
)
# Импортируем функцию для создания таблиц
from api.db import create_tables

# Настройка логирования
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Инициализация приложения Flask
app = Flask(__name__)

# Создания таблицы
create_tables()

# Регистрируем Blueprint для каждого API
app.register_blueprint(dashboard.dashboard_bp, url_prefix='/api')
app.register_blueprint(reviews.total_reviews_bp, url_prefix='/api')
app.register_blueprint(reviews.trend_reviews_bp, url_prefix='/api')
app.register_blueprint(ratings.ratings_distribution_bp, url_prefix='/api')
app.register_blueprint(ratings.ratings_trend_bp, url_prefix='/api')
app.register_blueprint(sentiment.sentiment_distribution_bp, url_prefix='/api')
app.register_blueprint(sentiment.sentiment_trend_bp, url_prefix='/api')
app.register_blueprint(
    change_subscription.change_subscription_bp, url_prefix='/api'
)
app.register_blueprint(
    create_restaurant.create_restaurant_bp, url_prefix='/api'
)
app.register_blueprint(
    edit_restaurant.edit_restaurant_bp, url_prefix='/api'
)

# Запуск приложения
if __name__ == '__main__':
    logger.info("Запуск Flask приложения на порту 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)
