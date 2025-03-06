from os import getenv

from aiogram import Router, Bot
from aiogram.types import CallbackQuery
from dotenv import load_dotenv

from data.read_data import read_rest_ya_reviews_date

load_dotenv()

router = Router()

ADMIN_ID = int(getenv('ADMIN_ID'))


@router.callback_query(lambda c: c.data == 'test_insigth')
async def test_insigth(callback_query: CallbackQuery, bot: Bot):
    """Обрабатываем запрос проверки инсайтов за прошедший месяц."""

    user_id = callback_query.from_user.id
    if user_id == ADMIN_ID:
        await callback_query.message.answer(
            text='Тесирую месячный инсайт для ресторана с id 1.'
        )
        period = '2025-02'
        # Извлекаем отзывы за прошедший месяц
        reviews_data = read_rest_ya_reviews_date(1, period)
        # Формируем список текстов отзывов
        reviews = [review.content for review in reviews_data]

        await callback_query.message.answer(
            text=reviews
        )
