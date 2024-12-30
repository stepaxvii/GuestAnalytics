import asyncio

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    FSInputFile,
    Message
)

from yandex.yandex_primary_collection import ya_prim_coll

router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message):
    """Обработчик стартовой команды и выбор действий."""

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='Яндекс', callback_data='yandex_link'
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
    total_count, doc_name = ya_prim_coll(original_url=user_link)

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
        'Подготавливаю файл к отправке.'
    )

    file_path = f'D:/review_pars/{doc_name}'

    try:
        file = FSInputFile(file_path)
        await message.answer_document(
            document=file,
            caption='Вот ваш файл с отзывами.'
        )
        print('Файл успешно отправлен.')
    except Exception as e:
        print(f'Ошибка при отправке файла: {e}')
        await message.answer('Произошла ошибка при отправке файла.')
