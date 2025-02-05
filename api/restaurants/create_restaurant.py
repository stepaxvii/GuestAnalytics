from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from data_base.data_main_two import RestaurantTwo, session_two

create_restaurant_bp = Blueprint("create_restaurant", __name__)


@create_restaurant_bp.route("/create_restaurant", methods=["POST"])
def create_restaurant():
    # Получаем данные из запроса
    data = request.get_json(force=True)

    rest_id = data.get("restaurant_id")
    rest_title = data.get("restaurant_name")
    rest_link = data.get("yandex_link")
    tg_id = data.get("telegram_id")
    action = data.get("action")

    # Проверяем, если действие это создание нового ресторана
    if action == "create":
        try:
            # Создаем новый ресторан в базе данных
            restaurant = RestaurantTwo(
                id=rest_id,
                title=rest_title,
                yandex_link=rest_link,
                address="default address",
                tg_channal=tg_id,
            )
            # Добавляем ресторан в сессию и сохраняем
            session_two.add(restaurant)
            session_two.commit()
            return jsonify({"status": "ok", "message": "Restaurant created successfully."}), 200
        except IntegrityError as e:
            session_two.rollback()
            print(f"Ошибка уникальности: {e}")
            return jsonify({"status": "error", "message": "Restaurant already exists."}), 400
        finally:
            session_two.close()

    # Если действие не является 'create', возвращаем ошибку
    return jsonify({"status": "error", "message": "Invalid action."}), 400
