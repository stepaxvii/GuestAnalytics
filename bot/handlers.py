import asyncio

from aiogram import Bot, Router
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    Message
)

from constants import TG_CHANNAL
from utils.message_text import get_star_rating
from yandex.yandex_primary_collection import ya_prim_coll
from yandex.yandex_check_new_reviews import matching_reviews

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
        text='Проверяю наличие новых отзывов для ресторана Lali'
    )
    await asyncio.sleep(1)

    # Получаем новые отзывы
    new_reviews = matching_reviews(
        'https://yandex.ru/maps/org/lali/107765078887/'
    )

    # Проверяем, есть ли новые отзывы
    if new_reviews:
        for review in new_reviews:
            # Форматируем сообщение для отправки
            message = (
                f"{get_star_rating(review[2])}\n"
                f"Яндекс, {review[0]}\n\n"
                f"{review[3]}\n"
                f"Автор: {review[1]}\n"
            )

            # Отправляем сообщение в канал
            await bot.send_message(TG_CHANNAL, message)

        await callback_query.message.answer(
            "Новые отзывы успешно отправлены в канал!"
        )
    else:
        await callback_query.message.answer("Новых отзывов нет.")


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
