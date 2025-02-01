import asyncio
import logging
from os import getenv

from aiogram import Bot
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from dotenv import load_dotenv

from data_base.read_data import read_all_restaurant_data
from utils.message_text import get_star_rating
from yandex.yandex_check_new_reviews import matching_reviews

load_dotenv()


async def check_new_reviews_periodically(bot: Bot):
    """Функция переодической проверки новых отзывов."""
    while True:
        try:
            # Пауза между проверками 1 час
            await asyncio.sleep(3600)
            logging.info("Функция для проверки новых отзывов")

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
                            f"{rest_title}, {rest_address}.\n"
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
            logging.error(f"Ошибка в периодической задаче: {e}")
