# import logging

# from flask import Flask
# from api.charts import (
#     dashboard,
#     ratings,
#     reviews,
#     sentiment
# )
# from api.restaurants import (
#     change_subscription,
#     create_restaurant,
#     edit_restaurant
# )
# # Импортируем функцию для создания таблиц
# from api.db import create_tables

# # Настройка логирования
# logging.basicConfig(level=logging.DEBUG)

# app = Flask(__name__)

# # Создаем таблицы, если их еще нет
# create_tables()

# # Регистрируем Blueprint для каждого API
# app.register_blueprint(dashboard.dashboard_bp, url_prefix='/api')
# app.register_blueprint(reviews.total_reviews_bp, url_prefix='/api')
# app.register_blueprint(reviews.trend_reviews_bp, url_prefix='/api')
# app.register_blueprint(ratings.ratings_distribution_bp, url_prefix='/api')
# app.register_blueprint(ratings.ratings_trend_bp, url_prefix='/api')
# app.register_blueprint(sentiment.sentiment_distribution_bp, url_prefix='/api')
# app.register_blueprint(sentiment.sentiment_trend_bp, url_prefix='/api')
# app.register_blueprint(
#     change_subscription.change_subscription_bp, url_prefix='/api'
# )
# app.register_blueprint(
#     create_restaurant.create_restaurant_bp, url_prefix='/api'
# )
# app.register_blueprint(
#     edit_restaurant.edit_restaurant_bp, url_prefix='/api'
# )

# app.logger.setLevel(logging.DEBUG)

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)
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
logging.basicConfig(level=logging.INFO)  # Устанавливаем уровень логирования INFO

app = Flask(__name__)

# Создаем таблицы, если их еще нет
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

# Настройка логирования для Flask
app.logger.setLevel(logging.INFO)


# Пример логирования для Flask
@app.route('/')
def hello_world():
    app.logger.info('Обработка запроса к корневому маршруту')
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
