import asyncio
from os import getenv

from aiogram import Bot, Router
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    Message
)
from dotenv import load_dotenv

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

                # Проверка наличия ссылки на автора
                if 'link' in review and review['link']:
                    # Если есть link, создаем кнопку с ссылкой на автора
                    button_text = "Перейти к автору"
                    button_url = review['link']
                else:
                    # Если link нет, создаем кнопку с ссылкой на отзывы
                    button_text = "Перейти к отзывам"
                    button_url = rest_reviews_link

                # Создаем кнопку с условной ссылкой
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(
                            text=button_text, url=button_url
                        )]
                    ]
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
