import asyncio
from datetime import datetime, timedelta
import logging
from os import getenv

from aiogram import Bot
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from dotenv import load_dotenv

from bot.handlers.report import send_monthly_report
from data.create_data import create_insight
from data.read_data import (
    read_all_restaurant_data,
    read_rest_month_insight,
    read_rest_twogis_reviews_date,
    read_rest_ya_reviews_date
)
from semantic_analysis.month_insight import month_insight
from utils.date import check_month, make_last_months
from utils.message_text import get_star_rating
from utils.semantic import make_count_insights
from twogis.twogis_check_new_reviews import twogis_matching_reviews
from yandex.yandex_check_new_reviews import ya_matching_reviews


load_dotenv()

ADMIN_ID = getenv("ADMIN_ID")


# Настройка логирования
logger = logging.getLogger()


async def check_ya_new_reviews_periodically(bot: Bot):
    """Функция переодической проверки новых отзывов Яндекс."""
    while True:
        try:
            # Пауза между проверками 1 час
            await asyncio.sleep(3600)
            logger.info("Функция для проверки новых отзывов Яндекс.")

            # Получаем данные о ресторанах
            restaurants = read_all_restaurant_data()

            for restaurant in restaurants:
                # rest_id = restaurant['id'] сделать для сравнения с БД
                rest_title = restaurant['title']
                rest_link = restaurant['yandex_link']
                rest_address = restaurant['address']
                rest_tg_channal = restaurant['tg_channal']
                rest_subscription = restaurant['subscription']
                rest_reviews_link = rest_link + 'reviews'

                # Проверяем активность подписки
                if rest_subscription is False:
                    # Если подписка неактивна - логгируем
                    logger.info(
                        "Подписка для ресторана "
                        f"{rest_title} ({rest_address}) неактивна.\n"
                        "‼️Необходимо продлить подписку."
                    )
                    continue  # Пропускаем проверку отзывов для этого ресторана
                new_reviews = ya_matching_reviews(rest_link)

                # Логируем количество новых отзывов
                logger.info(f"Найдено новых отзывов: {len(new_reviews)}")

                # Проверяем, есть ли новые отзывы
                if new_reviews:
                    for review in new_reviews:
                        # Логируем информацию о каждом отзыве
                        review_date_str = review['review_date']
                        review_date = datetime.strptime(
                            review_date_str, '%Y-%m-%d'
                        )
                        current_date = datetime.now()

                        # Проверяем, если дата отзыва старше, чем на 8 дней
                        if current_date - review_date >= timedelta(days=8):
                            logger.info(
                                f"Отзыв на {review_date_str} слишком стар."
                            )
                            continue  # Пропускаем отзыв, если он старше 8 дней

                        logger.info(
                            "Обрабатываем отзыв от "
                            f"{review.get('author_name', 'неизвестен' )}"
                        )
                        message = (
                            f"{rest_title}, <b>{rest_address}</b>.\n\n"
                            f"{get_star_rating(int(review['rating_value']))}\n"
                            f"\n{review['text']}\n\n"
                            f"Яндекс, {review['review_date']}\n"
                            # f"Автор: {review['author_name']}\n"
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
                                inline_keyboard=[[
                                    InlineKeyboardButton(
                                        text=button_text_1,
                                        url=button_url_1
                                    ),
                                    InlineKeyboardButton(
                                        text=button_text_2,
                                        url=button_url_2
                                    )
                                ]]
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
                            rest_tg_channal,
                            message,
                            reply_markup=keyboard
                        )
                        await asyncio.sleep(3)

            logger.info("Проверка новых отзывов Яндекс завершена.")

        except Exception as e:
            logger.error(f"Ошибка в периодической задаче отзывов Яндекс: {e}")


async def check_twogis_new_reviews_periodically(bot: Bot):
    """Функция периодической проверки новых отзывов 2ГИС."""
    while True:
        try:
            # Пауза между проверками 1.5 часа
            await asyncio.sleep(5427)
            logger.info("Функция для проверки новых отзывов 2ГИС.")

            # Получаем данные о ресторанах
            restaurants = read_all_restaurant_data()

            for restaurant in restaurants:
                # Проверяем, что ссылка на 2ГИС не пуста
                rest_link = restaurant.get('twogis_link')
                if not rest_link:
                    logger.info(
                        f"У ресторана {restaurant['title']} нет 2ГИС."
                    )
                    continue  # Пропускаем ресторан, если ссылки нет

                rest_title = restaurant['title']
                rest_address = restaurant['address']
                rest_tg_channal = restaurant['tg_channal']
                rest_subscription = restaurant['subscription']
                rest_reviews_link = rest_link + '/tab/reviews'

                # Проверяем активность подписки
                if rest_subscription is False:
                    # Если подписка неактивна - логгируем
                    logger.info(
                        "Подписка для ресторана "
                        f"{rest_title} ({rest_address}) неактивна.\n"
                        "‼️Необходимо продлить подписку."
                    )
                    continue  # Пропускаем проверку отзывов для этого ресторана

                # Получаем новые отзывы
                new_reviews = twogis_matching_reviews(rest_link)

                # Логируем количество новых отзывов
                logger.info(f"Найдено новых отзывов: {len(new_reviews)}")

                # Проверяем, есть ли новые отзывы
                if new_reviews:
                    for review in new_reviews:
                        # Логируем информацию о каждом отзыве
                        review_date_str = review['review_date']
                        review_date = datetime.strptime(
                            review_date_str, '%Y-%m-%d'
                        )
                        current_date = datetime.now()

                        # Проверяем, если дата отзыва старше, чем на 8 дней
                        if current_date - review_date >= timedelta(days=8):
                            logger.info(
                                f"Отзыв на {review_date_str} слишком стар."
                                )
                            continue  # Пропускаем отзыв, если он старше 8 дней

                        logger.info(
                            "Обрабатываем отзыв от "
                            f"{review.get('author_name', 'неизвестен' )}"
                        )
                        message = (
                            f"{rest_title}, <b>{rest_address}</b>.\n\n"
                            f"{get_star_rating(int(review['rating_value']))}\n"
                            f"\n{review['text']}\n\n"
                            f"2ГИС, {review['review_date']}\n"
                            # f"Автор: {review['author_name']}\n"
                        )

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

            logger.info("Проверка новых отзывов 2ГИС завершена.")

        except Exception as e:
            logger.error(f"Ошибка в периодической задаче отзывов 2ГИС: {e}")


async def check_new_insight_periodically(bot: Bot):
    """Функция для переодической проверки новых инсайтов."""
    while True:
        try:
            # Пауза между проверками 24 часа
            await asyncio.sleep(84640)
            logger.info("Функция для запуска анализов новых инсайтов.")
            await bot.send_message(
                chat_id=ADMIN_ID,
                text="Запуск периодической задачи инсайтов."
            )

            # Получаем текущий месяц для анализа
            current_date = datetime.now()
            if current_date.day == 3:

                # Получаем данные о ресторанах
                restaurants = read_all_restaurant_data()

                for restaurant in restaurants:
                    rest_id = restaurant['id']
                    rest_name = restaurant['title']
                    rest_subscription = restaurant['subscription']

                    # Проверяем активность подписки
                    if rest_subscription is False:
                        # Пропускаем проверку отзывов для этого ресторана
                        continue

                    # Проверяем наличие инсайтов в БД
                    last_month = make_last_months(
                        current_date=current_date
                    )[0]
                    insight = read_rest_month_insight(
                        restaurant_id=rest_id,
                        month=last_month
                    )

                    if not insight:
                        # Если записи инсайта нет, то нужно выполнить анализ
                        await bot.send_message(
                            chat_id=ADMIN_ID,
                            text=f"Инсайтов для '{rest_name}' в БД нет."
                        )
                        asyncio.sleep(1)

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
                        insight = month_insight(
                            reviews_block=reviews,
                            count_insights=count_reviews
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
                            logging.info("В БД содержится актуальный инсайт.")
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
                            await bot.send_message(
                                chat_id=ADMIN_ID,
                                text=f"2ГИС - {len(reviews_twogis)}\n"
                                f"Яндекс - {len(reviews_ya)}"
                            )

                            count_reviews = len(reviews)

                            if reviews:
                                await bot.send_message(
                                    chat_id=ADMIN_ID,
                                    text="Выявляю инсайты.\n"
                                    f"Всего отзывов {count_reviews}"
                                )
                                count_insights = make_count_insights(
                                    review_block=reviews
                                )
                                # Выполнение анализа инсайтов
                                insight = month_insight(
                                    reviews_block=reviews,
                                    count_insights=count_insights
                                    )
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

                # Отправляем отчёты в телеграм-каналы клиентов
                await send_monthly_report(bot=bot)

            else:
                await bot.send_message(
                    chat_id=ADMIN_ID,
                    text="Ещё рано запрашивать инсайты за прошлый месяц."
                )
            logger.info("Проверка новых инсайтов завершена.")

        except Exception as e:
            logger.error(f"Ошибка в периодической задаче с инсайтами: {e}")
