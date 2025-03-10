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

from data.read_data import (
    read_all_restaurant_data,
    read_rest_month_insight,
    read_rest_ya_reviews_date
)
from semantic_analysis.month_insight import month_insight
from utils.date import check_month
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
            # Пауза между проверками 30 минут
            await asyncio.sleep(1800)
            logging.info("Функция для запуска анализов новых инсайтов.")

            # Получаем данные о ресторанах
            restaurants = read_all_restaurant_data()

            for restaurant in restaurants:
                rest_id = restaurant['id']

                # Проверяем наличие инсайтов в БД
                insigth = read_rest_month_insight(restaurant_id=rest_id)
                if not insigth:
                    # Если записи инсайта нет, то нужно выполнить анализ
                    await bot.send_message(
                        chat_id=ADMIN_ID,
                        text="Записи инсайта нет. Проводится анализ отзывов."
                    )

                    # Получаем текущий месяц для анализа
                    current_month = datetime.now().strftime('%Y-%m')
                    # НУЖНО ПОПРАВИТЬ ЛОГИКУ ИНСАЙТОВ

                    # Извлекаем отзывы за текущий месяц
                    reviews_data = read_rest_ya_reviews_date(
                        restaurant_id=rest_id,
                        date_filter=current_month
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
                    insigth = "ИНСАЙТ"
                    await bot.send_message(
                        chat_id=ADMIN_ID,
                        text=insigth
                    )

                else:
                    # Если инсайт существует, проверяем его актуальность
                    last_month_insigth, last_month = check_month(insigth.period)
                    if last_month_insigth:
                        logging.info("-------WE HAVE A ACTUAL INSIGHT!-------")
                    else:
                        # Если инсайт устарел, нужно провести повторный анализ
                        await bot.send_message(
                            chat_id=ADMIN_ID,
                            text="Инсайт устарел. Проводится повторный анализ отзывов."
                        )

                        # Получаем текущий месяц для анализа
                        current_month = datetime.now().strftime('%Y-%m')

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
                        insigth = "ИНСАЙТ"
                        await bot.send_message(
                            chat_id=ADMIN_ID,
                            text=insigth
                        )

            logging.info("Проверка новых инсайтов завершена.")

        except Exception as e:
            logging.error(f"Ошибка в периодической задаче с инсайтами: {e}")


# async def check_new_insigth_periodically(bot: Bot):
#     """Функция переодической проверки новых инсайтов."""

#     while True:
#         try:
#             # Пауза между проверками 30 минут
#             await asyncio.sleep(1800)
#             logging.info("Функция для запуска анализов новых инсайтов.")

#             # Получаем данные о ресторанах
#             restaurants = read_all_restaurant_data()

#             for restaurant in restaurants:
#                 rest_id = restaurant['id']

#                 # Проверяем наличие инсайтов в БД
#                 insigth = read_rest_month_insight(restaurant_id=rest_id)
#                 if not insigth:
#                     # Если записи инсайта нет, то нужно выполнить анализ
#                     await bot.send_message(
#                         chat_id=ADMIN_ID,
#                         text="Записи инсайта нет. Проводится анализ отзывов."
#                     )

#                     # Извлекаем отзывы за прошедший месяц
#                     reviews_data = read_rest_ya_reviews_date(
#                         restaurant_id=rest_id,
#                         date_filter=last_month
#                     )
#                     reviews = [review.content for review in reviews_data]
#                     count_reviews = len(reviews)

#                     if reviews:
#                         await bot.send_message(
#                             chat_id=ADMIN_ID,
#                             text="Отправляю для выявления инсайтов.\n"
#                             f"Всего отзывов {count_reviews}"
#                         )
#                     else:
#                         await bot.send_message(
#                             chat_id=ADMIN_ID,
#                             text='Отзывов за указанный период не найдено.'
#                         )

#                     # Выполнение анализа инсайтов
#                     insigth = month_insight(reviews_block=reviews)
#                     await bot.send_message(
#                         chat_id=ADMIN_ID,
#                         text=insigth
#                     )

#                 else:
#                     # Если инсайт существует, проверяем его актуальность
#                     last_month_insigth, last_month = check_month(insigth.period)
#                     if last_month_insigth:
#                         logging("-------WE HAVE A ACTUAL INSIGHT!-------")
#                     else:
#                         # Если инсайт устарел, нужно провести повторный анализ
#                         await bot.send_message(
#                             chat_id=ADMIN_ID,
#                             text="Инсайт устарел. Проводится повторный анализ отзывов."
#                         )

#                         # Извлекаем отзывы за прошедший месяц
#                         reviews_data = read_rest_ya_reviews_date(restaurant_id=rest_id, date_filter=last_month)
#                         reviews = [review.content for review in reviews_data]
#                         count_reviews = len(reviews)

#                         if reviews:
#                             await bot.send_message(
#                                 chat_id=ADMIN_ID,
#                                 text="Отправляю для выявления инсайтов.\n"
#                                 f"Всего отзывов {count_reviews}"
#                             )
#                         else:
#                             await bot.send_message(
#                                 chat_id=ADMIN_ID,
#                                 text='Отзывов за указанный период не найдено.'
#                             )

#                         # Выполнение анализа инсайтов
#                         insigth = month_insight(reviews_block=reviews)
#                         await bot.send_message(
#                             chat_id=ADMIN_ID,
#                             text=insigth
#                         )

#             logging.info("Проверка новых инсайтов завершена.")

#         except Exception as e:
#             logging.error(f"Ошибка в периодической задаче с инсайтами: {e}")
