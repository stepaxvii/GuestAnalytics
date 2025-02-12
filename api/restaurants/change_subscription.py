import logging

from flask import Blueprint, request, jsonify
from api.db import session
from data.data_main import Restaurant

change_subscription_bp = Blueprint("change_subscription", __name__)


@change_subscription_bp.route("/change_subscription", methods=["POST"])
def change_subscription():
    # Получаем данные из запроса
    data = request.get_json(force=True)

    rest_id = data.get("restaurant_id")
    subscription = data.get("subscription")
    action = data.get("action")

    # Проверяем, если действие это обновление данных ресторана
    if action == "update":
        try:
            # Ищем ресторан по ID
            restaurant = session.query(Restaurant).filter_by(id=rest_id).first()
            if not restaurant:
                return jsonify(
                    {"status": "error", "message": "Ресторан не найден."}
                ), 404

            # Преобразуем subscription в булево значение
            if isinstance(subscription, str):
                # Обрабатываем строки "True", "False", "t", "f" и т.д.
                subscription = subscription.lower() in (
                    "true", "t", "yes", "y", "1"
                )
            elif isinstance(subscription, bool):
                pass  # Уже булево значение
            else:
                return jsonify(
                    {
                        "status": "error",
                        "message": "Некорректное значение для subscription."
                    }
                ), 400

            # Обновляем данные о подписке
            restaurant.subscription = subscription

            # Сохраняем изменения в базе данных
            session.commit()

            return jsonify(
                {"status": "ok", "message": "Данные о подписке изменены."}
            ), 200
        except Exception as e:
            session.rollback()
            logging.error(f"Произошла ошибка при обновлении данных: {e}")
            return jsonify(
                {
                    "status": "error",
                    "message": "Произошла ошибка при обновлении данных."
                }
            ), 500
        finally:
            session.close()

    # Если действие не является 'update', возвращаем ошибку
    return jsonify(
        {"status": "error", "message": "Некорректное действие."}
    ), 400
