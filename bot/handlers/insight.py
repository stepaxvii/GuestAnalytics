import asyncio
from datetime import datetime
import logging
from os import getenv

from aiogram import Router, Bot
from aiogram.types import CallbackQuery
from dotenv import load_dotenv

from data.create_data import create_insight
from data.read_data import (
    read_all_restaurant_data,
    read_rest_month_insight,
    read_rest_ya_reviews_date
)
from semantic_analysis.month_insight import month_insight
from utils.date import check_month, make_last_months
from utils.semantic import make_count_insights

load_dotenv()

router = Router()

ADMIN_ID = int(getenv('ADMIN_ID'))


async def check_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь администратором."""
    return user_id == ADMIN_ID


@router.callback_query(lambda c: c.data == 'test_insight')
async def test_insight(callback_query: CallbackQuery, bot: Bot):
    """Обрабатываем запрос проверки инсайтов за прошедший месяц."""

    if await check_admin(callback_query.from_user.id):
        await callback_query.message.answer(
            text='Тесирую месячный инсайт для ресторанов.'
        )

        logging.info("Функция для запуска анализов новых инсайтов.")

        # Получаем текущий месяц для анализа
        current_date = datetime.now()

        # Получаем данные о ресторанах
        restaurants = read_all_restaurant_data()

        for restaurant in restaurants:
            rest_id = restaurant['id']
            rest_name = restaurant['title']

            # Проверяем наличие инсайтов в БД
            insight = read_rest_month_insight(restaurant_id=rest_id)
            if not insight:
                # Если записи инсайта нет, то нужно выполнить анализ
                await bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"Инсайтов для '{rest_name}' в БД нет."
                )
                asyncio.sleep(1)

                last_month = make_last_months(current_date=current_date)[0]

                # Извлекаем отзывы за текущий месяц
                reviews_data = read_rest_ya_reviews_date(
                    restaurant_id=rest_id,
                    date_filter=last_month
                )
                reviews = [review.content for review in reviews_data]
                count_reviews = len(reviews)

                if reviews:
                    await bot.send_message(
                        chat_id=ADMIN_ID,
                        text="Отправляю для выявления инсайтов.\n"
                        f"Всего отзывов {count_reviews}"
                    )
                else:
                    await bot.send_message(
                        chat_id=ADMIN_ID,
                        text='Отзывов за указанный период не найдено.'
                    )

                # Выполнение анализа инсайтов
                count_insights = make_count_insights(review_block=reviews)
                insight = month_insight(
                    reviews_block=reviews, count_insights=count_insights
                )
                insight_data = (rest_id, last_month, insight)
                create_insight(data=insight_data)

                await bot.send_message(
                    chat_id=ADMIN_ID,
                    text=insight
                )

            else:
                # Если инсайт существует, проверяем его актуальность
                last_month_insight, last_month = check_month(
                    insight.period
                )
                if last_month_insight:
                    logging.info("-----WE HAVE A ACTUAL INSIGHT!-----")
                    await bot.send_message(
                        chat_id=ADMIN_ID,
                        text="В БД содержится актуальный инсайт.\n"
                        f"{last_month} - {insight.insight}"
                    )
                else:
                    # Если инсайт устарел, нужно провести новый анализ
                    await bot.send_message(
                        chat_id=ADMIN_ID,
                        text=f"Нет свежего инсайта за {last_month}"
                    )

                    # Извлекаем отзывы за текущий месяц
                    reviews_data = read_rest_ya_reviews_date(
                        restaurant_id=rest_id,
                        date_filter=last_month
                    )
                    reviews = [
                        review.content for review in reviews_data
                    ]
                    count_reviews = len(reviews)

                    if reviews:
                        await bot.send_message(
                            chat_id=ADMIN_ID,
                            text="Выявляю инсайты.\n"
                            f"Всего отзывов {count_reviews}"
                        )
                        # Выполнение анализа инсайтов
                        insight = month_insight(reviews_block=reviews)
                        insight_data = (rest_id, last_month, insight)
                        create_insight(data=insight_data)

                        await bot.send_message(
                            chat_id=ADMIN_ID,
                            text=insight
                        )

                    else:
                        await bot.send_message(
                            chat_id=ADMIN_ID,
                            text='Отзывов за период не найдено.'
                        )
        logging.info("Проверка новых инсайтов завершена.")
