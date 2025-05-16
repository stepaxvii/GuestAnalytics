import asyncio
from os import getenv

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
)
from dotenv import load_dotenv

from api.db import session
from bot.states import RestaurantEditState
from data.data_main import Restaurant
from data.read_data import read_all_restaurant_data
from twogis.twogis_primary_collection import twogis_prim_coll
from utils.urls import check_full_url

load_dotenv()
router = Router()

ADMIN_ID = int(getenv('ADMIN_ID'))


async def check_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь администратором."""
    return user_id == ADMIN_ID


@router.callback_query(lambda c: c.data == 'data_edit')
async def handle_data_edit(callback_query: Message):
    if await check_admin(callback_query.from_user.id):
        # Получаем все рестораны
        restaurants_list = read_all_restaurant_data()

        # Проверяем, есть ли рестораны
        if not restaurants_list:
            await callback_query.answer("Нет доступных ресторанов.")
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
        await callback_query.message.answer(
            "Выберите ресторан для редактирования:", reply_markup=keyboard
        )


@router.callback_query(lambda c: c.data.startswith('data_edit_rest_'))
async def edit_restaurant(callback_query: CallbackQuery, state: FSMContext):
    if await check_admin(callback_query.from_user.id):
        restaurant_id = int(callback_query.data.split('_')[-1])
        # Удаляем сообщение с клавиатурой
        await callback_query.message.delete()

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
                        text="wordpress ID",
                        callback_data="edit_wp_id"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="добавить 2ГИС",
                        callback_data="edit_add_twogis"
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
    if await check_admin(callback_query.from_user.id):
        # Переходим к состоянию редактирования названия
        await state.set_state(RestaurantEditState.title_edit)
        # Удаляем сообщение с клавиатурой
        await callback_query.message.delete()

        await callback_query.message.answer("Введите новое название:")


@router.callback_query(lambda c: c.data == "edit_address")
async def edit_address(callback_query: CallbackQuery, state: FSMContext):
    if await check_admin(callback_query.from_user.id):
        # Переходим к состоянию редактирования адреса
        await state.set_state(RestaurantEditState.address_edit)
        # Удаляем сообщение с клавиатурой
        await callback_query.message.delete()

        await callback_query.message.answer("Введите новый адрес ресторана:")


@router.callback_query(lambda c: c.data == "edit_tg_channal")
async def edit_tg_channal(callback_query: CallbackQuery, state: FSMContext):
    if await check_admin(callback_query.from_user.id):
        # Переходим к состоянию редактирования tg_channal
        await state.set_state(RestaurantEditState.tg_channal_edit)
        # Удаляем сообщение с клавиатурой
        await callback_query.message.delete()

        await callback_query.message.answer("Введите новый TG канал:")


@router.callback_query(lambda c: c.data == "edit_wp_id")
async def edit_wp_id(callback_query: CallbackQuery, state: FSMContext):
    if await check_admin(callback_query.from_user.id):
        # Переходим к состоянию редактирования wp_id_edit
        await state.set_state(RestaurantEditState.wp_id_edit)
        # Удаляем сообщение с клавиатурой
        await callback_query.message.delete()

        await callback_query.message.answer("Введите изменённый wp_id:")


@router.callback_query(lambda c: c.data == "edit_add_twogis")
async def edit_add_twogis(callback_query: CallbackQuery, state: FSMContext):
    if await check_admin(callback_query.from_user.id):
        # Переходим к состоянию редактирования add_twogis
        await state.set_state(RestaurantEditState.add_twogis)
        # Удаляем сообщение с клавиатурой
        await callback_query.message.delete()

        await callback_query.message.answer("Введите url 2ГИС:")


@router.message(RestaurantEditState.title_edit)
async def save_title(message: Message, state: FSMContext):
    if await check_admin(message.from_user.id):
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
                await message.answer("Ошибка при изменении данных")

        # Завершаем редактирование
        await state.clear()
        await message.answer("Редактирование завершено.")


@router.message(RestaurantEditState.address_edit)
async def save_address(message: Message, state: FSMContext):
    if await check_admin(message.from_user.id):
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
                await message.answer("Ошибка при изменении данных")

        # Завершаем редактирование
        await state.clear()
        await message.answer("Редактирование завершено.")


@router.message(RestaurantEditState.tg_channal_edit)
async def save_tg_channal(message: Message, state: FSMContext):
    if await check_admin(message.from_user.id):
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
                await message.answer("Ошибка при изменении данных")

        # Завершаем редактирование
        await state.clear()
        await message.answer("Редактирование завершено.")


@router.message(RestaurantEditState.wp_id_edit)
async def save_wp_id(message: Message, state: FSMContext):
    if await check_admin(message.from_user.id):
        new_wp_id = message.text.strip()

        if new_wp_id:
            data = await state.get_data()
            restaurant_id = data.get("restaurant_id")

            # Обновляем wp_id в базе данных
            restaurant = session.query(
                Restaurant
            ).filter(Restaurant.id == restaurant_id).first()

            if restaurant:
                restaurant.wp_id = new_wp_id
                session.commit()
                await message.answer(f"Wordpress ID обновлён на {new_wp_id}")
            else:
                await message.answer("Ошибка при изменении данных")

        # Завершаем редактирование
        await state.clear()
        await message.answer("Редактирование завершено.")


@router.message(RestaurantEditState.add_twogis)
async def save_twogis_link(message: Message, state: FSMContext):
    if await check_admin(message.from_user.id):
        new_twogis_link = message.text.strip()

        if new_twogis_link:
            data = await state.get_data()
            restaurant_id = data.get("restaurant_id")

            restaurant = session.query(
                Restaurant
            ).filter(Restaurant.id == restaurant_id).first()
            if restaurant:
                twogis_link_save = check_full_url(user_url=new_twogis_link)
                restaurant.twogis_link = twogis_link_save
                session.commit()
                await message.answer(
                    "Ссылка 2ГИС сохранена."
                )
                await message.answer(
                    "Начинаю первичный сбор отзывов."
                )
                twogis_prim_coll(url=twogis_link_save, rest_id=restaurant_id)
                await message.answer(
                    "Первичный сбор отзывов завершён."
                )
            else:
                await message.answer("Ошибка при изменении данных")

        # Завершаем редактирование
        await state.clear()
        await message.answer("Редактирование завершено")


@router.callback_query(lambda c: c.data == "restaurant_delete")
async def delete_restaurant(callback_query: CallbackQuery, state: FSMContext):
    if await check_admin(callback_query.from_user.id):
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
