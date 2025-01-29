from flask import Flask, jsonify, request

app = Flask(__name__)


# 1) /api/total-reviews
@app.route('/api/total-reviews', methods=['GET'])
def total_reviews():
    user_id = int(request.args.get('user_id'))
    print(f"------{user_id}----------")
    if not user_id:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан user_id"
        }), 400

    if user_id == 1:

        total_reviews = 234
        percentage_change = 100.2  # Условно +10.2%

    if user_id == 2:

        total_reviews = 432
        percentage_change = 30.2  # Условно +10.2%

    return jsonify({
        "success": True,
        "data": {
            "total_reviews": total_reviews,
            "percentage_change": percentage_change
        },
        "message": "Данные по total-reviews получены"
    }), 200


# 2) /api/trend-reviews
@app.route('/api/trend-reviews', methods=['GET'])
def trend_reviews():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан user_id"
        }), 400

    # Пример данных
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


# 3) /api/ratings-distribution
@app.route('/api/ratings-distribution', methods=['GET'])
def ratings_distribution():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан user_id"
        }), 400

    # Пример данных
    data = {
        "labels": ["5 звёзд", "4 звезды", "3 звезды", "2 звезды", "1 звезда"],
        "values": [50, 30, 10, 5, 5]
    }

    return jsonify({
        "success": True,
        "data": data,
        "message": "Данные по ratings-distribution получены"
    }), 200


# 4) /api/ratings-trend
@app.route('/api/ratings-trend', methods=['GET'])
def ratings_trend():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан user_id"
        }), 400

    # Пример данных: несколько серий (5 звёзд, 4 звёзды и т.п.)
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


# 5) /api/sentiment-distribution
@app.route('/api/sentiment-distribution', methods=['GET'])
def sentiment_distribution():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан user_id"
        }), 400

    # Пример данных
    data = {
        "labels": ["Положительные", "Нейтральные", "Отрицательные"],
        "values": [70, 20, 10]
    }

    return jsonify({
        "success": True,
        "data": data,
        "message": "Данные по sentiment-distribution получены"
    }), 200


# 6) /api/sentiment-trend
@app.route('/api/sentiment-trend', methods=['GET'])
def sentiment_trend():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Не указан user_id"
        }), 400

    # Пример данных: 3 линии — Положительные, Нейтральные, Отрицательные
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


# -- Запуск приложения --
if __name__ == '__main__':
    # Запуск на порту 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
