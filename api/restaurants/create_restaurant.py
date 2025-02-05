from flask import Blueprint, request, jsonify


create_restaurant_test_bp = Blueprint('create_restaurant_test', __name__)


@create_restaurant_test_bp.route('/create_restaurant', methods=['GET'])
def create_restaurant_test():
    rest_id = request.args.get('restaurant_id')
    rest_title = request.args.get('restaurant_name')
    rest_link = request.args.get('yandex_link')
    print(f'id = {rest_id}')
    print(f'title - {rest_title}')
    print(f'link - {rest_link}')

    return jsonify({"status": "ok"}), 200


# # http://217.114.9.10:5000/api/create_restaurant


create_restaurant_bp = Blueprint("create_restaurant", __name__)


@create_restaurant_bp.route("/create_restaurant", methods=["POST"])
def create_restaurant():
    data = request.get_json(force=True)
    # Если вдруг пришёл не JSON, force=True заставит попытаться распарсить

    rest_id = data.get("restaurant_id")
    rest_title = data.get("restaurant_name")
    rest_link = data.get("yandex_link")
    tg_id = data.get("telegram_id")
    action = data.get("action")

    print("=== CREATE_RESTAURANT endpoint called ===")
    print(f"action: {action}")
    print(f"restaurant_id: {rest_id}")
    print(f"restaurant_name: {rest_title}")
    print(f"yandex_link: {rest_link}")
    print(f"telegram_id: {tg_id}")

    return jsonify({"status": "ok"}), 200
