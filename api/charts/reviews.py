from flask import Blueprint, jsonify, request

trend_reviews_bp = Blueprint('trend_reviews', __name__)


@trend_reviews_bp.route('/trend-reviews', methods=['GET'])
def trend_reviews():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан user_id"
        }), 400

    data = {
        "labels": ["Январь", "Февраль", "Март", "Апрель"],
        "dataset": {
            "label": "Отзывы",
            "data": [100, 120, 140, 160],
            "borderColor": "#36A2EB"
        }
    }

    return jsonify({
        "success": True,
        "data": data,
        "message": "Данные по trend-reviews получены"
    }), 200


total_reviews_bp = Blueprint('total_reviews', __name__)


@total_reviews_bp.route('/total-reviews', methods=['GET'])
def total_reviews():
    user_id = int(request.args.get('user_id'))
    if not user_id:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан user_id"
        }), 400

    if user_id == 1:
        total_reviews = 234
        percentage_change = 100.2

    if user_id == 2:
        total_reviews = 432
        percentage_change = 30.2

    return jsonify({
        "success": True,
        "data": {
            "total_reviews": total_reviews,
            "percentage_change": percentage_change
        },
        "message": "Данные по total-reviews получены"
    }), 200
