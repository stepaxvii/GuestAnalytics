from os import getenv

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
)
from aiogram.filters import Command
from dotenv import load_dotenv

from api.db import session
from bot.states import RestaurantEditState
from data.data_main import Restaurant
from data.read_data import read_all_restaurant_data

load_dotenv()
router = Router()

ADMIN_ID = int(getenv('ADMIN_ID'))


@router.message(Command('data_edit'))
async def handle_data_edit(message: Message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        # Получаем все рестораны с помощью вашей функции
        restaurants_list = read_all_restaurant_data()

        # Проверяем, есть ли рестораны
        if not restaurants_list:
            await message.answer("Нет доступных ресторанов для изменения.")
            return

        # Генерируем клавиатуру с кнопками для каждого ресторана
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"{restaurant['title']} {restaurant['address']}",
                        callback_data=f"data_edit_rest_{restaurant['id']}"
                    )
                ] for restaurant in restaurants_list
            ]
        )

        # Отправляем сообщение с клавиатурой
        await message.answer(
            "Выберите ресторан для редактирования:", reply_markup=keyboard
        )


@router.callback_query(lambda c: c.data.startswith('data_edit_rest_'))
async def edit_restaurant(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if user_id == ADMIN_ID:
        restaurant_id = int(callback_query.data.split('_')[-1])

        # Сохраняем id ресторана в состоянии
        await state.update_data(restaurant_id=restaurant_id)

        # Генерируем клавиатуру с кнопками для выбора действия
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="название",
                        callback_data="edit_title"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="адрес",
                        callback_data="edit_address"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="TG-канал",
                        callback_data="edit_tg_channal"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="удалить ресторан",
                        callback_data="restaurant_delete"
                    )
                ]
            ]
        )

        await callback_query.message.answer(
            "Что вы хотите изменить в ресторане?",
            reply_markup=keyboard
        )


@router.callback_query(lambda c: c.data == "edit_title")
async def edit_title(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if user_id == ADMIN_ID:
        # Переходим к состоянию редактирования названия
        await state.set_state(RestaurantEditState.title_edit)

        await callback_query.message.answer("Введите новое название:")


@router.callback_query(lambda c: c.data == "edit_address")
async def edit_address(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if user_id == ADMIN_ID:
        # Переходим к состоянию редактирования адреса
        await state.set_state(RestaurantEditState.address_edit)

        await callback_query.message.answer("Введите новый адрес ресторана:")


@router.callback_query(lambda c: c.data == "edit_tg_channal")
async def edit_tg_channal(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if user_id == ADMIN_ID:
        # Переходим к состоянию редактирования tg_channal
        await state.set_state(RestaurantEditState.tg_channal_edit)

        await callback_query.message.answer("Введите новый TG канал:")


@router.message(RestaurantEditState.title_edit)
async def save_title(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        new_title = message.text.strip()

        if new_title:
            data = await state.get_data()
            restaurant_id = data.get("restaurant_id")

            # Обновляем название в базе данных
            restaurant = session.query(
                Restaurant
            ).filter(Restaurant.id == restaurant_id).first()

            if restaurant:
                restaurant.title = new_title
                session.commit()
                await message.answer(f"Название обновлено на {new_title}.")
            else:
                await message.answer("Ресторан не найден.")

        # Завершаем редактирование
        await state.clear()
        await message.answer("Редактирование завершено.")


@router.message(RestaurantEditState.address_edit)
async def save_address(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        new_address = message.text.strip()

        if new_address:
            data = await state.get_data()
            restaurant_id = data.get("restaurant_id")

            # Обновляем адрес в базе данных
            restaurant = session.query(
                Restaurant
            ).filter(Restaurant.id == restaurant_id).first()

            if restaurant:
                restaurant.address = new_address
                session.commit()
                await message.answer(f"Адрес обновлён на {new_address}.")
            else:
                await message.answer("Ресторан не найден.")

        # Завершаем редактирование
        await state.clear()
        await message.answer("Редактирование завершено.")


@router.message(RestaurantEditState.tg_channal_edit)
async def save_tg_channal(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        new_tg_channal = message.text.strip()

        if new_tg_channal:
            data = await state.get_data()
            restaurant_id = data.get("restaurant_id")

            # Обновляем TG канал в базе данных
            restaurant = session.query(
                Restaurant
            ).filter(Restaurant.id == restaurant_id).first()

            if restaurant:
                restaurant.tg_channal = new_tg_channal
                session.commit()
                await message.answer(f"TG канал обновлён на {new_tg_channal}.")
            else:
                await message.answer("Ресторан не найден.")

        # Завершаем редактирование
        await state.clear()
        await message.answer("Редактирование завершено.")


@router.callback_query(lambda c: c.data == "restaurant_delete")
async def delete_restaurant(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if user_id == ADMIN_ID:
        data = await state.get_data()
        restaurant_id = data.get("restaurant_id")

        # Ищем ресторан в базе данных по ID
        restaurant = session.query(
            Restaurant
        ).filter(Restaurant.id == restaurant_id).first()

        if restaurant:
            # Удаляем ресторан из базы данных
            session.delete(restaurant)
            session.commit()

            await callback_query.message.answer(
                f"Ресторан с ID {restaurant_id} был удалён."
            )
        else:
            await callback_query.message.answer("Ресторан не найден.")

        # Завершаем редактирование
        await state.clear()
        await callback_query.message.answer("Редактирование завершено.")
