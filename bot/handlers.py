import asyncio
from os import getenv

from aiogram import Bot, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    Message
)
from dotenv import load_dotenv

from bot.bot_main import RestaurantEditState
from data_base.data_main import session, Restaurant
from data_base.read_data import read_all_restaurant_data
from utils.message_text import get_star_rating
from yandex.yandex_primary_collection import ya_prim_coll
from yandex.yandex_check_new_reviews import matching_reviews


load_dotenv()

TG_GROUP = getenv('TG_GROUP')

router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message):
    """Обработчик стартовой команды и выбор действий."""

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='Яндекс', callback_data='yandex_link'
            )],
            [InlineKeyboardButton(
                text='проверить новые отзывы', callback_data='check_new'
            )]
        ]
    )
    await message.answer(
        text='Обработчик старта. Выберите действие.',
        reply_markup=keyboard
    )


@router.callback_query(lambda c: c.data == 'yandex_link')
async def get_yandex_link(callback_query: CallbackQuery):
    """Обрабатываем ссылку на Яндекс."""
    await callback_query.message.answer(
        text='Отправьте ссылку на заведение с Яндекс.Карт.\n'
             'Формат: "https://yandex.ru/maps/org..."'
    )


@router.callback_query(lambda c: c.data == 'check_new')
async def check_new_ya_reviews(callback_query: CallbackQuery, bot: Bot):
    """Обрабатываем запрос проверки новых отзывов"""
    await callback_query.message.answer(
        text='Проверяю наличие новых отзывов для ресторанов партнёров.'
    )
    await asyncio.sleep(1)

    restaurants = read_all_restaurant_data()

    for restaurant in restaurants:
        rest_title = restaurant['title']
        rest_link = restaurant['yandex_link']
        rest_address = restaurant['address']
        rest_reviews_link = rest_link + 'reviews'

        # Получаем новые отзывы
        new_reviews = matching_reviews(rest_link)

        # Проверяем, есть ли новые отзывы
        if new_reviews:
            for review in new_reviews:
                # Форматируем сообщение для отправки
                message = (
                    f"{rest_title}, {rest_address}.\n"
                    f"{get_star_rating(review['rating_value'])}\n"
                    f"Яндекс, {review['review_date']}\n\n"
                    f"{review['text']}\n"
                    f"Автор: {review['author_name']}\n"
                    f"Семантика - \"{review.get('semantic')}\""
                )

                if (
                    'author_link' in review
                    and review['author_link']
                    and review['author_link'] != 'None'
                ):
                    # Если ссылка на автора есть
                    # и не равна 'None', создаем обе кнопки
                    button_text_1 = "К автору"
                    button_url_1 = review['author_link']
                    button_text_2 = " К отзывам"
                    button_url_2 = rest_reviews_link

                    keyboard = InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(
                                    text=button_text_1,
                                    url=button_url_1
                                ),
                                InlineKeyboardButton(
                                    text=button_text_2,
                                    url=button_url_2
                                )
                            ]
                        ]
                    )
                else:
                    button_text = "Перейти к отзывам"
                    button_url = rest_reviews_link

                    keyboard = InlineKeyboardMarkup(
                        inline_keyboard=[[InlineKeyboardButton(
                            text=button_text, url=button_url
                        )]]
                    )

                # Отправляем сообщение в канал
                await bot.send_message(
                    TG_GROUP, message, reply_markup=keyboard
                )
                await asyncio.sleep(3)

            await callback_query.message.answer(
                f"Новые отзывы для ресторана {rest_title} отправлены в канал!"
            )
        else:
            await callback_query.message.answer(
                f"Новых отзывов для ресторана {rest_title} нет."
            )


@router.message(
        lambda message: message.text.startswith('https://yandex.ru/maps/')
)
async def validate_link(message: Message):
    """Проверка ссылки на валидность и возврат готовой ссылки."""

    user_link = message.text

    await asyncio.sleep(1)
    await message.answer(
        'Начинаю анализ отзывов за весь период.'
    )

    await asyncio.sleep(2)

    await message.answer('Скоро вернусь)')

    # Вызываем функцию анализа отзывов
    total_count = ya_prim_coll(original_url=user_link)

    if not total_count:
        # Если функция вернула False, оповещаем пользователя
        await message.answer(
            'Произошла ошибка при обработке ссылки.\n'
            'Пожалуйста, предоставьте ссылку ещё раз.'
        )
        # Повторная отправка кнопки для новой ссылки
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text='Попробовать снова', url='https://yandex.ru/maps/org'
                )]
            ]
        )
        await message.answer(
            text='Пожалуйста, отправьте корректную ссылку.\n'
                 'Для этого перейдите в Яндекс Карты '
                 'и поделитесь с ботом ссылкой',
            reply_markup=keyboard
        )
        return

    # Если анализ прошел успешно
    await message.answer(
        'Анализ завершён.\n'
        f'Проанализировано отзывов: {total_count}. '
    )


@router.message(commands=['data_edit'])
async def handle_data_edit(message: Message):
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
                    text=restaurant['title'],  # Название ресторана
                    callback_data=f"data_edit_restaurant_{restaurant['id']}"
                )
            ] for restaurant in restaurants_list
        ]
    )

    # Отправляем сообщение с клавиатурой
    await message.answer(
        "Выберите ресторан для редактирования:", reply_markup=keyboard
    )


@router.callback_query(lambda c: c.data.startswith('data_edit_restaurant_'))
async def edit_restaurant(callback_query: CallbackQuery, state: FSMContext):
    restaurant_id = int(callback_query.data.split('_')[-1])

    # Сохраняем id ресторана в состоянии
    await state.update_data(restaurant_id=restaurant_id)

    # Генерируем клавиатуру с кнопками для выбора действия
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Изменить название", callback_data="edit_title"),
                InlineKeyboardButton(text="Изменить адрес", callback_data="edit_address"),
                InlineKeyboardButton(text="Изменить TG канал", callback_data="edit_tg_channal")
            ]
        ]
    )

    await callback_query.message.answer(
        "Что вы хотите изменить в ресторане?",
        reply_markup=keyboard
    )


@router.callback_query(lambda c: c.data == "edit_title")
async def edit_title(callback_query: CallbackQuery, state: FSMContext):
    # Переходим к состоянию редактирования названия
    await state.set_state(RestaurantEditState.title_edit)

    await callback_query.message.answer("Введите новое название ресторана:")


@router.callback_query(lambda c: c.data == "edit_address")
async def edit_address(callback_query: CallbackQuery, state: FSMContext):
    # Переходим к состоянию редактирования адреса
    await state.set_state(RestaurantEditState.address_edit)

    await callback_query.message.answer("Введите новый адрес ресторана:")


@router.callback_query(lambda c: c.data == "edit_tg_channal")
async def edit_tg_channal(callback_query: CallbackQuery, state: FSMContext):
    # Переходим к состоянию редактирования tg_channal
    await state.set_state(RestaurantEditState.tg_channal_edit)

    await callback_query.message.answer("Введите новый TG канал ресторана:")


@router.message(RestaurantEditState.title_edit)
async def save_title(message: Message, state: FSMContext):
    new_title = message.text.strip()

    if new_title:
        data = await state.get_data()
        restaurant_id = data.get("restaurant_id")

        # Обновляем название в базе данных
        restaurant = session.query(Restaurant).filter(Restaurant.id == restaurant_id).first()

        if restaurant:
            restaurant.title = new_title
            session.commit()
            await message.answer(f"Название ресторана обновлено на {new_title}.")
        else:
            await message.answer("Ресторан не найден.")

    # Завершаем редактирование
    await state.finish()
    await message.answer("Редактирование завершено.")


@router.message(RestaurantEditState.address_edit)
async def save_address(message: Message, state: FSMContext):
    new_address = message.text.strip()

    if new_address:
        data = await state.get_data()
        restaurant_id = data.get("restaurant_id")

        # Обновляем адрес в базе данных
        restaurant = session.query(Restaurant).filter(Restaurant.id == restaurant_id).first()

        if restaurant:
            restaurant.address = new_address
            session.commit()
            await message.answer(f"Адрес ресторана обновлен на {new_address}.")
        else:
            await message.answer("Ресторан не найден.")

    # Завершаем редактирование
    await state.finish()
    await message.answer("Редактирование завершено.")


@router.message(RestaurantEditState.tg_channal_edit)
async def save_tg_channal(message: Message, state: FSMContext):
    new_tg_channal = message.text.strip()

    if new_tg_channal:
        data = await state.get_data()
        restaurant_id = data.get("restaurant_id")

        # Обновляем TG канал в базе данных
        restaurant = session.query(Restaurant).filter(Restaurant.id == restaurant_id).first()

        if restaurant:
            restaurant.tg_channal = new_tg_channal
            session.commit()
            await message.answer(f"TG канал ресторана обновлен на {new_tg_channal}.")
        else:
            await message.answer("Ресторан не найден.")
    
    # Завершаем редактирование
    await state.finish()
    await message.answer("Редактирование завершено.")
