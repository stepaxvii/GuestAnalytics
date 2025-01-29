from flask import Blueprint, jsonify, request

ratings_distribution_bp = Blueprint('ratings_distribution', __name__)


@ratings_distribution_bp.route('/ratings-distribution', methods=['GET'])
def ratings_distribution():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан user_id"
        }), 400

    data = {
        "labels": ["5 звёзд", "4 звезды", "3 звезды", "2 звезды", "1 звезда"],
        "values": [50, 30, 10, 5, 5]
    }

    return jsonify({
        "success": True,
        "data": data,
        "message": "Данные по ratings-distribution получены"
    }), 200


ratings_trend_bp = Blueprint('ratings_trend', __name__)


@ratings_trend_bp.route('/ratings-trend', methods=['GET'])
def ratings_trend():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан user_id"
        }), 400

    data = {
        "labels": ["Январь", "Февраль", "Март", "Апрель"],
        "datasets": [
            {
                "label": "5 звёзд",
                "data": [20, 22, 25, 27],
                "borderColor": "#2ECC71"
            },
            {
                "label": "4 звезды",
                "data": [10, 14, 18, 20],
                "borderColor": "#3498DB"
            },
            {
                "label": "3 звезды",
                "data": [5, 7, 9, 6],
                "borderColor": "#9B59B6"
            },
            {
                "label": "2 звезды",
                "data": [3, 2, 4, 5],
                "borderColor": "#F1C40F"
            },
            {
                "label": "1 звезда",
                "data": [2, 3, 1, 2],
                "borderColor": "#E74C3C"
            }
        ]
    }

    return jsonify({
        "success": True,
        "data": data,
        "message": "Данные по ratings-trend получены"
    }), 200
