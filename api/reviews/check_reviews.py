import logging

from flask import Blueprint, request, jsonify
from yandex.yandex_primary_collection_api import ya_prim_coll


yandex_prim_coll_bp = Blueprint("yandex_prim_coll", __name__)


@yandex_prim_coll_bp.route("/yandex_prim_coll", methods=["POST"])
def yandex_prim_coll():
    # Получаем данные из запроса
    data = request.get_json(force=True)

    rest_id = data.get("restaurant_id")

    # Проверяем, если действие это "create"
    action = data.get("action")

    if action == "create":
        try:
            # Вызываем ya_prim_coll с переданным ID ресторана
            ya_prim_coll(rest_id)

            return jsonify(
                {"status": "ok", "message": "Start checking with Yandex."}
            ), 200
        except Exception as e:
            logging.error(f"Error occurred while calling ya_prim_coll: {e}")
            return jsonify(
                {"status": "error", "message": str(e)}
            ), 500

    # Если действие не является 'create', возвращаем ошибку
    return jsonify({"status": "error", "message": "Invalid action."}), 400
