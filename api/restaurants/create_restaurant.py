from flask import Blueprint, request


create_restaurant_bp = Blueprint('create_restaurant', __name__)


@create_restaurant_bp.route('/create_restaurant', methods=['GET'])
def create_restaurant():
    rest_id = request.args.get('restaurant_id')
    rest_title = request.args.get('restaurant_name')
    rest_link = request.args.get('yandex_link')
    print(f'id = {rest_id}')
    print(f'title - {rest_title}')
    print(f'link - {rest_link}')


# http://217.114.9.10:5000/api/create_restaurant