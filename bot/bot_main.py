# import asyncio
# import logging
# import sys
# from os import getenv
# from dotenv import load_dotenv
# from aiogram import Bot, Dispatcher
# from aiogram.client.default import DefaultBotProperties
# from aiogram.enums import ParseMode
# from aiogram.fsm.state import State, StatesGroup

# from bot import handlers, periodically_tasks

# load_dotenv()

# # Из окружения извлекаем необходимые токены, ключи и переменные
# TELEGRAM_TOKEN = getenv('TELEGRAM_TOKEN')


# class LinkFMS(StatesGroup):
#     """Определение состояния FMS."""
#     yandex_link = State()
#     twogis_link = State()


# async def main():
#     bot = Bot(
#         token=TELEGRAM_TOKEN,
#         default=DefaultBotProperties(parse_mode=ParseMode.HTML)
#     )
#     dp = Dispatcher()
#     dp.include_router(handlers.router)

#     # Запуск фоновой задачи для проверки новых отзывов
#     periodic_task = asyncio.create_task(
#         periodically_tasks.check_new_reviews_periodically(bot)
#     )

#     try:
#         await bot.delete_webhook(drop_pending_updates=True)
#         await dp.start_polling(bot)
#         # Дожидаемся завершения фоновой задачи
#         # (если она не завершится по ошибке)
#         await periodic_task
#     except Exception as error:
#         logging.error(f"Произошла ошибка: {error}")


# if __name__ == "__main__":
#     logging.basicConfig(
#         level=logging.INFO,
#         stream=sys.stdout,
#     )
#     asyncio.run(main())


import asyncio
import logging
import sys
from os import getenv
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.state import State, StatesGroup
from flask import Flask, Response
from sqlalchemy.orm import sessionmaker
from data_base.data_main import YandexReview, engine
import json
from aiohttp import web
from bot import handlers, periodically_tasks

# Загружаем переменные окружения
load_dotenv()
TELEGRAM_TOKEN = getenv('TELEGRAM_TOKEN')

# Создаем Flask-приложение
app = Flask(__name__)

# Настройка сессии для работы с базой данных
Session = sessionmaker(bind=engine)
session = Session()


@app.route('/api/first-yandex-author', methods=['GET'])
async def get_first_yandex_author():
    first_review = session.query(YandexReview).first()

    if first_review:
        data = json.dumps({
            "success": True,
            "author": first_review.author
        }, ensure_ascii=False)
        return Response(data, mimetype='application/json')
    else:
        data = json.dumps({
            "success": False,
            "message": "No reviews found"
        }, ensure_ascii=False)
        return Response(data, mimetype='application/json')


class LinkFMS(StatesGroup):
    """Определение состояния FMS."""
    yandex_link = State()
    twogis_link = State()


async def main():
    # Создаем Telegram-бота
    bot = Bot(
        token=TELEGRAM_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.include_router(handlers.router)

    # Запуск фоновой задачи для проверки новых отзывов
    periodic_task = asyncio.create_task(
        periodically_tasks.check_new_reviews_periodically(bot)
    )

    # Запускаем Flask-приложение в отдельном потоке
    flask_task = asyncio.create_task(run_flask_app())

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
        await periodic_task
    except Exception as error:
        logging.error(f"Произошла ошибка: {error}")

    # Дожидаемся завершения фоновой задачи Flask
    await flask_task


async def run_flask_app():
    """Запуск Flask приложения на асинхронном сервере aiohttp."""
    # Запуск Flask-приложения через aiohttp
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 5000)
    await site.start()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
    )
    asyncio.run(main())
