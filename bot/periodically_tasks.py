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

TG_GROUP = getenv('TG_GROUP')


# Функция для проверки новых отзывов
async def check_new_reviews_periodically(bot: Bot):
    while True:
        try:
            # Пауза между проверками
            await asyncio.sleep(2000)  # 2000 секунд = 33 минуты
            print("Функция для проверки новых отзывов")

            # Получаем данные о ресторанах
            restaurants = read_all_restaurant_data()

            for restaurant in restaurants:
                rest_title = restaurant['title']
                rest_link = restaurant['yandex_link']
                rest_address = restaurant['address']
                rest_reviews_link = rest_link + 'reviews'

                # Получаем новые отзывы
                new_reviews = matching_reviews(rest_link)

                # Проверяем, есть ли новые отзывы
                if new_reviews:
                    for review in new_reviews:
                        # Форматируем сообщение для отправки
                        message = (
                            f"{rest_title}, {rest_address}.\n"
                            f"{get_star_rating(review['rating_value'])}\n"
                            f"Яндекс, {review['review_date']}\n\n"
                            f"{review['text']}\n"
                            f"Автор: {review['author_name']}\n"
                            f"Семантика - \"{review.get('semantic')}\""
                        )

                        # Проверка наличия ссылки на автора
                        if 'link' in review and review['link']:
                            # Если есть link, создаем кнопку с ссылкой на автора
                            button_text = "Перейти к автору"
                            button_url = review['link']
                        else:
                            # Если link нет, создаем кнопку с ссылкой на отзывы
                            button_text = "Перейти к отзывам"
                            button_url = rest_reviews_link

                        # Создаем кнопку с условной ссылкой
                        keyboard = InlineKeyboardMarkup(
                            inline_keyboard=[
                                [InlineKeyboardButton(
                                    text=button_text, url=button_url
                                )]
                            ]
                        )

                        # Отправляем сообщение в канал
                        await bot.send_message(
                            TG_GROUP, message, reply_markup=keyboard
                        )
                        await asyncio.sleep(3)

            logging.info("Проверка новых отзывов завершена.")

        except Exception as e:
            logging.error(f"Ошибка в периодической задаче: {e}")
