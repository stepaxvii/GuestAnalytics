import asyncio
from os import getenv

from aiogram import Router, Bot
from aiogram.types import (
    CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
)
from dotenv import load_dotenv

from data.read_data import read_all_restaurant_data
from utils.message_text import get_star_rating
from yandex.yandex_primary_collection import ya_prim_coll
from yandex.yandex_check_new_reviews_api import matching_reviews
from bot.handlers.report import send_monthly_report

load_dotenv()

router = Router()

ADMIN_ID = int(getenv('ADMIN_ID'))


async def check_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь администратором."""
    return user_id == ADMIN_ID


@router.callback_query(lambda c: c.data == 'check_new')
async def check_new_ya_reviews(callback_query: CallbackQuery, bot: Bot):
    """Обрабатываем запрос проверки новых отзывов"""

    if await check_admin(callback_query.from_user.id):
        await callback_query.message.answer(
            text='Проверяю наличие новых отзывов для ресторанов партнёров.'
        )
        await asyncio.sleep(1)

        restaurants = read_all_restaurant_data()

        for restaurant in restaurants:
            rest_title = restaurant['title']
            rest_link = restaurant['yandex_link']
            rest_address = restaurant['address']
            rest_tg_channal = restaurant['tg_channal']
            rest_subscription = restaurant['subscription']
            rest_reviews_link = rest_link + 'reviews'

            # # Проверяем активность подписки
            if rest_subscription is False:
                # Если подписка неактивна, отправляем сообщение в канал
                await bot.send_message(
                    chat_id=rest_tg_channal,  # ID канала
                    text=(
                        f"Подписка для ресторана {rest_title} неактивна. "
                        "Необходимо продлить подписку для проверки отзывов."
                    )
                )
                continue  # Пропускаем проверку отзывов для этого ресторана

            # Если подписка активна, продолжаем проверку отзывов
            new_reviews = matching_reviews(rest_link)

            # Проверяем, есть ли новые отзывы
            if new_reviews:
                for review in new_reviews:
                    # Форматируем сообщение для отправки
                    message = (
                        f"{rest_title}, <b>{rest_address}</b>.\n"
                        f"{get_star_rating(review['rating_value'])}\n"
                        f"Яндекс, {review['review_date']}\n\n"
                        f"{review['text']}\n\n"
                        f"Автор: {review['author_name']}\n"
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
                        rest_tg_channal, message, reply_markup=keyboard
                    )
                    await asyncio.sleep(3)

                await callback_query.message.answer(
                    f"Новые отзывы для {rest_title} отправлены в канал!"
                )
            else:
                await callback_query.message.answer(
                    f"Новых отзывов для ресторана {rest_title} нет."
                )
        await send_monthly_report(bot)


@router.message(
    lambda message: message.text
    and message.text.startswith('https://yandex.ru/maps/')
)
async def validate_link(message: Message):
    """Проверка ссылки на валидность и возврат готовой ссылки."""
    if await check_admin(message.from_user.id):
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
                inline_keyboard=[[
                    InlineKeyboardButton(
                        text='Попробовать снова',
                        url='https://yandex.ru/maps/org'
                    )
                ]]
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
            f'Проанализировано отзывов: {total_count}.'
        )
