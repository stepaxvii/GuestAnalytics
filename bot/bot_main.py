import asyncio
import logging
import sys
from os import getenv
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot import periodically_tasks
from bot.handlers import start_router, yandex_router, data_edit_router

load_dotenv()

# Из окружения извлекаем необходимые токены, ключи и переменные
TELEGRAM_TOKEN = getenv('TELEGRAM_TOKEN')


async def main():
    bot = Bot(
        token=TELEGRAM_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.include_routers(
        data_edit_router,
        start_router,
        yandex_router
    )

    # Запуск фоновой задачи для проверки новых отзывов
    periodic_task = asyncio.create_task(
        periodically_tasks.check_new_reviews_periodically(bot)
    )

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
        # Дожидаемся завершения фоновой задачи
        # (если она не завершится по ошибке)
        await periodic_task
    except Exception as error:
        logging.error(f"Произошла ошибка: {error}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
    )
    asyncio.run(main())
