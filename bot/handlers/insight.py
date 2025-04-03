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
    read_rest_twogis_reviews_date,
    read_rest_ya_reviews_date
)
from semantic_analysis.month_insight import month_insight
from utils.date import check_month, make_last_months
from utils.semantic import make_count_insights

load_dotenv()

router = Router()

ADMIN_ID = int(getenv('ADMIN_ID'))

# Настроим базовое логирование
logging.basicConfig(level=logging.INFO)


async def check_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь администратором."""
    return user_id == ADMIN_ID


@router.callback_query(lambda c: c.data == 'test_insight')
async def test_insight(callback_query: CallbackQuery, bot: Bot):
    """Обрабатываем запрос проверки инсайтов за прошедший месяц."""

    if await check_admin(callback_query.from_user.id):
        await callback_query.message.answer(
            text='Тестирую месячный инсайт для ресторанов.'
        )

        logging.info("Запуск тестирования инсайтов для ресторанов...")

        current_date = datetime.now()

        # Получаем все рестораны для анализа
        restaurants = read_all_restaurant_data()

        for restaurant in restaurants:
            rest_id = restaurant['id']
            rest_name = restaurant['title']

            # Проверяем наличие инсайтов для ресторана в БД
            insight = read_rest_month_insight(restaurant_id=rest_id)
            if not insight:
                logging.info(f"Инсайтов для ресторана '{rest_name}' нет в БД.")

                await bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"Инсайтов для ресторана '{rest_name}' в БД нет."
                )

                # Получаем последний месяц для анализа
                last_month = make_last_months(current_date=current_date)[0]

                # Извлекаем отзывы за предыдущий месяц
                reviews_data_ya = read_rest_ya_reviews_date(
                    restaurant_id=rest_id,
                    date_filter=last_month
                    )
                reviews_ya = [
                    review.content for review in reviews_data_ya
                ]
                reviews_data_twogis = read_rest_twogis_reviews_date(
                    restaurant_id=rest_id,
                    date_filter=last_month
                )
                reviews_twogis = [
                    review.content for review in reviews_data_twogis
                ]
                reviews = reviews_ya + reviews_twogis
                count_reviews = len(reviews)

                if reviews:
                    logging.info(
                        f"Всего {count_reviews} отзывов для ресторана "
                        f"'{rest_name}' за месяц {last_month}."
                    )
                    await bot.send_message(
                        chat_id=ADMIN_ID,
                        text=f"Отправляю данные для выявления инсайтов.\n"
                        f"Всего отзывов: {count_reviews}"
                    )
                else:
                    logging.warning(
                        f"Отзывов за месяц {last_month} "
                        f"для ресторана '{rest_name}' не найдено."
                    )
                    await bot.send_message(
                        chat_id=ADMIN_ID,
                        text=f"Отзывов за месяц {last_month} "
                        f"для ресторана '{rest_name}' не найдено."
                    )

                # Выполнение анализа инсайтов
                count_insights = make_count_insights(review_block=reviews)
                insight_text = month_insight(
                    reviews_block=reviews, count_insights=count_insights
                )
                insight_data = (rest_id, last_month, insight_text)
                create_insight(data=insight_data)

                await bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"Инсайт для ресторана '{rest_name}':\n{insight_text}"
                )

            else:
                # Проверка актуальности инсайта
                last_month_insight, last_month = check_month(insight.period)
                if last_month_insight:
                    logging.info(
                        f"Найден актуальный инсайт для '{rest_name}'."
                    )
                    await bot.send_message(
                        chat_id=ADMIN_ID,
                        text="В БД есть актуальный инсайт для "
                        f"'{rest_name}' за {last_month}.\n{insight.insight}"
                    )
                else:
                    logging.info(
                        f"Инсайт для '{rest_name}' устарел. "
                        "Проводим новый анализ."
                    )

                    # Извлекаем отзывы за последний месяц
                    reviews_data = read_rest_ya_reviews_date(
                        restaurant_id=rest_id,
                        date_filter=last_month
                    )
                    reviews = [review.content for review in reviews_data]
                    count_reviews = len(reviews)

                    if reviews:
                        logging.info(
                            f"Всего {count_reviews} отзывов для "
                            f"'{rest_name}' за месяц {last_month}."
                        )
                        await bot.send_message(
                            chat_id=ADMIN_ID,
                            text=f"Обновляю инсайты для '{rest_name}'.\n"
                            f"Всего отзывов: {count_reviews}"
                        )

                        # Выполнение нового анализа инсайтов
                        count_insights = make_count_insights(
                            review_block=reviews
                        )
                        insight_text = month_insight(
                            reviews_block=reviews,
                            count_insights=count_insights
                        )
                        insight_data = (rest_id, last_month, insight_text)
                        create_insight(data=insight_data)

                        await bot.send_message(
                            chat_id=ADMIN_ID,
                            text="Инсайт для "
                            f"'{rest_name}':\n{insight_text}"
                        )
                    else:
                        logging.warning(
                            f"Отзывов за месяц {last_month} для "
                            f"'{rest_name}' не найдено."
                        )
                        await bot.send_message(
                            chat_id=ADMIN_ID,
                            text=f"Отзывов за месяц {last_month} для "
                            f"'{rest_name}' не найдено."
                        )

        logging.info("Проверка и создание инсайтов завершена.")
