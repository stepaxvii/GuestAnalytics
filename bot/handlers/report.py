import asyncio
import logging
from os import getenv

from aiogram import Router, Bot
from aiogram.types import CallbackQuery
from dotenv import load_dotenv

from data.read_data import read_all_restaurant_data
from utils.message_text import star_for_report
from utils.monthly_report_tg import (
    avg_rest_rating,
    count_reviews_by_rating,
    get_count_reviews
)
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
                f"2ГИС: {avg_twogis}\n\n"
                f"<b>Количество отзывов по каждому рейтингу:</b>\n"
            )

            # Подсчитываем количество отзывов с разным рейтингом
            rating_count = count_reviews_by_rating(restaurant_id=rest_id)

            # Сортируем по ключам (рейтингам) от 1 до 5
            sorted_ratings = sorted(rating_count.items(), reverse=True)

            # Добавляем информацию о каждом рейтинге в сообщение
            rating_text = ""
            for rating, count in sorted_ratings:
                rating_text += f"{rating} {star_for_report(rating)} - {count}\n"

            # Заключаем в спойлер
            message += f"<details><summary>📊 Рейтинг по звёздам</summary>\n{rating_text}</details>"

            await callback_query.bot.send_message(
                chat_id=rest_tg_channal,
                text=message
            )
            logger.info(f"Отчёт для ресторана {rest_title} отправлен!")
            await asyncio.sleep(3)

        logger.info("Тест отчёта завершён)")
