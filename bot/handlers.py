import asyncio
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    FSInputFile,
    Message
)
from bot.bot_main import LinkFMS
from utils.urls import process_url
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
        text='Обработчик старта.',
        reply_markup=keyboard
    )

@router.callback_query(lambda c: c.data == 'yandex_link')
async def get_yandex_link(callback_query: CallbackQuery):
    """Обрабатываем ссылку на Яндекс."""
    await callback_query.message.answer(
        text='Отправь ссылку с Яндекс.Карт.\n'
              'Формата "https://yandex.ru/maps/org..."'
    )

@router.message(lambda message: message.text.startswith('https://yandex.ru/maps/org/'))
async def validate_link(message: Message):
    """Проверка ссылки на валидность и возврат готовой ссылки."""
    
    link = message.text  # Получаем текст сообщения
    print(f"Первоначальная ссылка: {link}")
    
    valid_link = process_url(link)  # Обработка ссылки
    print(f"Готовая ссылка: {valid_link}")
    
    await message.answer("Ваша ссылка готова.\nНачинаю анализ отзывов за весь период.")
    
    await asyncio.sleep(2)  # Используйте await для асинхронного ожидания
    
    await message.answer("Анализирую.")
    
    total_count = ya_prim_coll(url=valid_link)
    
    await message.answer("Анализ завершён.\n"
                         f"Проанализировано отзывов: {total_count}. Подготавливаю файл к отправке.")
    
    file_path = 'D:/review_pars/ya_docs.txt'
    
    try:
        file = FSInputFile(file_path)
        await message.answer_document(document=file, caption='Вот ваш файл с отзывами.')
        print("Файл успешно отправлен.")
    except Exception as e:
        print(f"Ошибка при отправке файла: {e}")
        await message.answer("Произошла ошибка при отправке файла.")
