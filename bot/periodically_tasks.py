import asyncio

from aiogram import Bot

from constants import TG_CHANNAL, TG_ID
from data_base.read_data import read_all_restaurant_data
from utils.message_text import get_star_rating
from yandex.yandex_check_new_reviews import matching_reviews


# Функция для проверки новых отзывов
async def check_new_reviews_periodically(bot: Bot):
    while True:
        # Пауза между проверками
        await asyncio.sleep(2000)
        print("Функция для проверки новых отзывов")

        # Получаем данные о ресторанах
        restaurants = read_all_restaurant_data()

        for restaurant in restaurants:
            rest_title = restaurant['title']
            rest_link = restaurant['yandex_link']
            rest_address = restaurant['address']

            # Получаем новые отзывы
            new_reviews = matching_reviews(rest_link)

            # Проверяем, есть ли новые отзывы
            if new_reviews:
                for review in new_reviews:
                    # Форматируем сообщение для отправки
                    message = (
                        f"{rest_title}, {rest_address}.\n"
                        f"{get_star_rating(review[2])}\n"
                        f"Яндекс, {review[0]}\n\n"
                        f"{review[3]}\n"
                        f"Автор: {review[1]}\n"
                    )

                    # Отправляем сообщение в канал
                    await bot.send_message(TG_CHANNAL, message)
                    await asyncio.sleep(3)
            else:
                await bot.send_message(
                    TG_ID,
                    text=f"Новых отзывов для {rest_title} нет ("
                )

        print("Проверка новых отзывов завершена.")
