import logging
from threading import Thread

from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError

from api.db import session
from data.data_main import Restaurant
from utils.urls import check_full_url_yandex, process_url_yandex
from yandex.yandex_primary_collection_api import ya_prim_coll

create_restaurant_bp = Blueprint("create_restaurant", __name__)


# Функция для обработки yandex_link и создания ресторана в БД
def process_restaurant_creation(restaurant_data):
    rest_id = restaurant_data["restaurant_id"]
    rest_title = restaurant_data["restaurant_name"]
    rest_link = restaurant_data["yandex_link"]
    rest_address = restaurant_data["address"]
    tg_id = restaurant_data["telegram_id"]

    # Приводим yandex_link к необходимому виду
    rest_link = check_full_url_yandex(rest_link)
    org_url, reviews_url = process_url_yandex(rest_link)
    rest_link = org_url

    # Создаем новый ресторан в базе данных
    try:
        restaurant = Restaurant(
            id=rest_id,
            title=rest_title,
            yandex_link=rest_link,  # Сохраняем org_url
            address=rest_address,
            tg_channal=tg_id,
        )
        # Добавляем ресторан в сессию и сохраняем
        session.add(restaurant)
        session.commit()

        # Запускаем функцию в отдельном потоке для работы с yandex_link
        thread = Thread(target=run_yandex_check, args=(reviews_url, rest_id))
        thread.start()

    except IntegrityError as e:
        session.rollback()
        logging.info(f"Ошибка уникальности: {e}")
        raise ValueError("Restaurant already exists.")
    finally:
        session.close()


# Функция для выполнения долгой задачи в фоне
def run_yandex_check(reviews_url, restaurant_id):
    try:
        ya_prim_coll(reviews_url=reviews_url, rest_id=restaurant_id)
    except Exception as e:
        logging.error(f"Error occurred while calling ya_prim_coll: {e}")


@create_restaurant_bp.route("/create_restaurant", methods=["POST"])
def create_restaurant():
    # Получаем данные из запроса
    data = request.get_json(force=True)

    action = data.get("action")

    # Проверяем, если действие это создание нового ресторана
    if action == "create":
        try:
            # Запускаем создание ресторана в отдельном потоке
            thread = Thread(target=process_restaurant_creation, args=(data,))
            thread.start()

            return jsonify(
                {"status": "ok", "message": "Restaurant creation in progress."}
            ), 200
        except ValueError as e:
            return jsonify(
                {"status": "error", "message": str(e)}
            ), 400

    # Если действие не является 'create', возвращаем ошибку
    return jsonify({"status": "error", "message": "Invalid action."}), 400
