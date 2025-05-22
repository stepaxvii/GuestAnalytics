from os import getenv
import logging

from aiogram import Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

router = Router()

ADMIN_ID = int(getenv('ADMIN_ID'))

# Настройка логирования
logger = logging.getLogger()


async def check_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь администратором."""
    return user_id == ADMIN_ID


@router.message(CommandStart())
async def command_start_handler(message: Message):
    """Обработчик стартовой команды и выбор действий."""
    logger.info(
        f"Получена команда /start от пользователя {message.from_user.id}"
    )

    if await check_admin(message.from_user.id):
        logger.info(
            f"Пользователь {message.from_user.id} является администратором."
        )

        # Кнопки для меню
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='Проверить новые отзывы',
                        callback_data='check_new'
                    )
                ],
                [
                    InlineKeyboardButton(
                        text='Редактировать ресторан',
                        callback_data='data_edit'
                    )
                ],
                [
                    InlineKeyboardButton(
                        text='Тестовый инсайт',
                        callback_data='test_insight'
                    )
                ],
                [
                    InlineKeyboardButton(
                        text='Тестовый отчёт',
                        callback_data='test_report'
                    )
                ]
            ]
        )

        # Отправка сообщения с кнопками
        await message.answer(
            text='Обработчик старта. Выберите действие.',
            reply_markup=keyboard
        )

        logger.info(
            f"Меню отправлено пользователю {message.from_user.id}."
        )
    else:
        logger.warning(
            f"Пользователь {message.from_user.id} не является администратором."
        )
        await message.answer(text="Вы не имеете доступа к этой команде.")
