from os import getenv

from aiogram import Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart
from dotenv import load_dotenv


load_dotenv()
router = Router()

ADMIN_ID = int(getenv('ADMIN_ID'))


@router.message(CommandStart())
async def command_start_handler(message: Message):
    """Обработчик стартовой команды и выбор действий."""
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='проверить новые отзывы',
                        callback_data='check_new'
                    )
                ],
                [
                    InlineKeyboardButton(
                        text='редактировать ресторан',
                        callback_data='data_edit'
                    )
                ],
                [
                    InlineKeyboardButton(
                        text='test insitgh',
                        callback_data='test_insigth'
                    )
                ]
            ]
        )
        await message.answer(
            text='Обработчик старта. Выберите действие.',
            reply_markup=keyboard
        )
