from aiogram.fsm.state import State, StatesGroup


# Модуль с состояниями
class RestaurantEditState(StatesGroup):
    title_edit = State()
    address_edit = State()
    tg_channal_edit = State()
    wp_id_edit = State()
