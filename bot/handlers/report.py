import asyncio
import logging
from os import getenv

from aiogram import Router, Bot
from aiogram.types import CallbackQuery
from dotenv import load_dotenv

from data.read_data import read_all_restaurant_data
from utils.monthly_report_tg import avg_rest_rating, get_count_reviews

load_dotenv()

router = Router()

ADMIN_ID = int(getenv('ADMIN_ID'))

# Настройка логирования
logger = logging.getLogger()


async def check_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь администратором."""
    return user_id == ADMIN_ID


@router.callback_query(lambda c: c.data == 'test_report')
async def test_report(callback_query: CallbackQuery, bot: Bot):
    """Тестируем работу ежемесячного отчёта."""

    if await check_admin(callback_query.from_user.id):
        await callback_query.answer(
            text="Запускаю тест месячного отчёта"
        )

        # Получаем данные о ресторанах
        restaurants = read_all_restaurant_data()
        for restaurant in restaurants:
            rest_id = restaurant['id']
            rest_title = restaurant['title']
            rest_address = restaurant['address']
            rest_tg_channal = -1002453477756

            total, twogis, yandex = get_count_reviews(restaurant_id=rest_id)
            avg_total, avg_twogis, avg_yandex = avg_rest_rating(
                restaurant_id=rest_id
            )

            logger.info(f"Отчёт для ресторана {rest_title} готов!")

            # Формируем сообщение для отправки в телеграм
            message = (
                f"{rest_title}, <b>{rest_address}</b>.\n\n"
                f"<b>Общее количество</b>: {total}\n"
                f"Яндекс: {yandex}\n"
                f"2ГИС: {twogis}\n\n"
                f"<b>Средний рейтинг</b>: {avg_total}\n"
                f"Яндекс: {avg_yandex}\n"
                f"2ГИС: {avg_twogis}\n"
            )
            await callback_query.bot.send_message(
                chat_id=rest_tg_channal,
                text=message
            )
            logger.info(f"Отчёт для ресторана {rest_title} отправлен!")
            await asyncio.sleep(3)

        logger.info("Тест отчёта завершён)")
