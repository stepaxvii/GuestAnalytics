from flask import Blueprint, jsonify, request

sentiment_distribution_bp = Blueprint('sentiment_distribution', __name__)


@sentiment_distribution_bp.route('/sentiment-distribution', methods=['GET'])
def sentiment_distribution():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан user_id"
        }), 400

    data = {
        "labels": ["Положительные", "Нейтральные", "Отрицательные"],
        "values": [70, 20, 10]
    }

    return jsonify({
        "success": True,
        "data": data,
        "message": "Данные по sentiment-distribution получены"
    }), 200


sentiment_trend_bp = Blueprint('sentiment_trend', __name__)


@sentiment_trend_bp.route('/sentiment-trend', methods=['GET'])
def sentiment_trend():
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
                "label": "Положительные",
                "data": [50, 60, 55, 70],
                "borderColor": "#2ECC71"
            },
            {
                "label": "Нейтральные",
                "data": [30, 25, 30, 20],
                "borderColor": "#1E90FF"
            },
            {
                "label": "Отрицательные",
                "data": [20, 15, 15, 10],
                "borderColor": "#FF6347"
            }
        ]
    }

    return jsonify({
        "success": True,
        "data": data,
        "message": "Данные по sentiment-trend получены"
    }), 200
