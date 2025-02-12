# import logging
# from threading import Thread

# from flask import Blueprint, request, jsonify

# from data.read_data import read_some_id
# from yandex.yandex_primary_collection_api import ya_prim_coll


# yandex_prim_coll_bp = Blueprint("yandex_prim_coll", __name__)


# # Функция для выполнения долгой задачи в фоне
# def run_yandex_check(yandex_link, restaurant_id):
#     try:
#         ya_prim_coll(original_url=yandex_link, rest_id=restaurant_id)
#     except Exception as e:
#         logging.error(f"Error occurred while calling ya_prim_coll: {e}")


# @yandex_prim_coll_bp.route("/yandex_prim_coll", methods=["POST"])
# def yandex_prim_coll():
#     # Получаем данные из запроса
#     data = request.get_json(force=True)

#     restaurant_id = data.get("restaurant_id")
#     action = data.get("action")

#     if action == "create":
#         try:
#             # Проверяем ссылку
#             rest_data = read_some_id(restaurant_id)
#             yandex_link = rest_data['yandex_link']

#             # Запускаем выполнение функции в отдельном потоке
#             thread = Thread(
#                 target=run_yandex_check, args=(yandex_link, restaurant_id)
#             )
#             thread.start()

#             return jsonify(
#                 {"status": "ok", "message": "Start checking with Yandex."}
#             ), 200
#         except Exception as e:
#             logging.error(f"Error occurred while calling ya_prim_coll: {e}")
#             return jsonify(
#                 {"status": "error", "message": str(e)}
#             ), 500

#     return jsonify({"status": "error", "message": "Invalid action."}), 400


# # Уже существующий Blueprint
# yandex_coll_bp = Blueprint("yandex_coll", __name__)


# # Маршрут для получения ответа "OK"
# @yandex_coll_bp.route("/ok", methods=["GET"])
# def ok():
#     return jsonify({"status": "ok"}), 200
