import asyncio
from datetime import datetime
import logging
from os import getenv

from aiogram import Bot
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from dotenv import load_dotenv

from data.create_data import create_insight
from data.read_data import (
    read_all_restaurant_data,
    read_rest_month_insight,
    read_rest_ya_reviews_date
)
from semantic_analysis.month_insight import month_insight
from utils.date import check_month, make_last_month
from utils.message_text import get_star_rating
from yandex.yandex_check_new_reviews import matching_reviews


load_dotenv()

ADMIN_ID = getenv("ADMIN_ID")


async def check_new_reviews_periodically(bot: Bot):
    """Функция переодической проверки новых отзывов."""
    while True:
        try:
            # Пауза между проверками 1 час
            await asyncio.sleep(3600)
            logging.info("Функция для проверки новых отзывов.")

            # Получаем данные о ресторанах
            restaurants = read_all_restaurant_data()

            for restaurant in restaurants:
                # rest_id = restaurant['id'] сделать для сравнения с БД
                rest_title = restaurant['title']
                rest_link = restaurant['yandex_link']
                rest_address = restaurant['address']
                rest_tg_channal = restaurant['tg_channal']
                rest_reviews_link = rest_link + 'reviews'

                # Получаем новые отзывы
                new_reviews = matching_reviews(rest_link)

                # Логируем количество новых отзывов
                logging.info(f"Найдено новых отзывов: {len(new_reviews)}")

                # Проверяем, есть ли новые отзывы
                if new_reviews:
                    for review in new_reviews:
                        # Логируем информацию о каждом отзыве
                        logging.info(
                            "Обрабатываем отзыв от "
                            f"{review.get('author_name', 'неизвестен' )}"
                        )
                        message = (
                            f"{rest_title}, <b>{rest_address}</b>.\n"
                            f"{get_star_rating(int(review['rating_value']))}\n"
                            f"Яндекс, {review['review_date']}\n\n"
                            f"{review['text']}\n\n"
                            f"Автор: {review['author_name']}\n"
                        )

                        if (
                            'author_link' in review
                            and review['author_link']
                            and review['author_link'] != 'None'
                        ):
                            # Если ссылка на автора есть
                            # и не равна 'None', создаем обе кнопки
                            button_text_1 = "К автору"
                            button_url_1 = review['author_link']
                            button_text_2 = " К отзывам"
                            button_url_2 = rest_reviews_link

                            keyboard = InlineKeyboardMarkup(
                                inline_keyboard=[
                                    [
                                        InlineKeyboardButton(
                                            text=button_text_1,
                                            url=button_url_1
                                        ),
                                        InlineKeyboardButton(
                                            text=button_text_2,
                                            url=button_url_2
                                        )
                                    ]
                                ]
                            )
                        else:
                            button_text = "Перейти к отзывам"
                            button_url = rest_reviews_link

                            keyboard = InlineKeyboardMarkup(
                                inline_keyboard=[[InlineKeyboardButton(
                                    text=button_text, url=button_url
                                )]]
                            )

                        # Отправляем сообщение в канал
                        await bot.send_message(
                            rest_tg_channal, message, reply_markup=keyboard
                        )
                        await asyncio.sleep(3)

            logging.info("Проверка новых отзывов завершена.")

        except Exception as e:
            logging.error(f"Ошибка в периодической задаче отзывов: {e}")


async def check_new_insigth_periodically(bot: Bot):
    """Функция для переодической проверки новых инсайтов."""
    while True:
        try:
            # Пауза между проверками 12 часов
            await asyncio.sleep(43200)
            logging.info("Функция для запуска анализов новых инсайтов.")

            # Получаем текущий месяц для анализа
            current_date = datetime.now()
            if current_date.day == 3:

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

                        last_month = make_last_month(current_date=current_date)

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
                        insight = month_insight(reviews_block=reviews)
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

            else:
                await bot.send_message(
                    chat_id=ADMIN_ID,
                    text="Ещё рано запрашивать инсайты за прошлый месяц."
                )
            logging.info("Проверка новых инсайтов завершена.")

        except Exception as e:
            logging.error(f"Ошибка в периодической задаче с инсайтами: {e}")
