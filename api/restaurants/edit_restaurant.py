import logging

from flask import Blueprint, request, jsonify
from api.db import session
from data.data_main import Restaurant

edit_restaurant_bp = Blueprint("edit_restaurant", __name__)


@edit_restaurant_bp.route("/edit_restaurant", methods=["POST"])
def edit_restaurant():
    # Получаем данные из запроса
    data = request.get_json(force=True)

    wp_id = data.get("restaurant_id")
    rest_title = data.get("restaurant_name")
    rest_address = data.get("address")
    tg_id = data.get("telegram_id")
    action = data.get("action")

    # Проверяем, если действие это обновление данных ресторана
    if action == "update":
        try:
            # Ищем ресторан по ID
            restaurant = session.query(
                Restaurant
            ).filter_by(wp_id=wp_id).first()
            if not restaurant:
                return jsonify(
                    {"status": "error", "message": "Ресторан не найден."}
                ), 404

            # Обновляем данные ресторана (кроме id и yandex_link)
            if rest_title:
                restaurant.title = rest_title
            if rest_address:
                restaurant.address = rest_address
            if tg_id:
                restaurant.tg_channal = tg_id

            # Сохраняем изменения в базе данных
            session.commit()

            return jsonify(
                {"status": "ok", "message": "Данные успешно обновлены."}
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
