import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
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
# Импорт тестовых функций планировщика
from bot.periodically_tasks import (
    send_result_day_task, send_result_hour_task, send_result_month_task
)

# Настройка логирования
logging.basicConfig(level=logging.WARNING)

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


def monthly_task_insigth():
    """Ежемесячный запрос инсайтов."""

    today = datetime.today()
    if today.day == 10:
        logging.info("Запускаем анализ инсайтов.")

    else:
        logging.info(f"Сегодня {today.day}.")


schelduler = BackgroundScheduler()

# Ежечасная задача
schelduler.add_job(
    func=send_result_hour_task,
    trigger='interval',
    hours=1
)


# Ежедневная задача
schelduler.add_job(
    func=send_result_day_task,
    trigger='interval',
    day=1
)

# Ежемесячная задача
schelduler.add_job(
    func=send_result_month_task,
    trigger='cron',
    day=10,
    hour=0,
    minute=0
)

schelduler.start()


@app.teardown_appcontext
def shutdown_schelduler(exception=None):
    if schelduler.running:
        schelduler.shutdown()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
