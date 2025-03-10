import asyncio
from datetime import datetime
from functools import partial
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

from bot import periodically_tasks
from bot.handlers import start, yandex, data_edit, insigth
from bot.periodically_tasks import (
    send_result_day_task, send_result_hour_task, send_result_month_task
)

load_dotenv()

# Из окружения извлекаем необходимые токены, ключи и переменные
TELEGRAM_TOKEN = getenv('TELEGRAM_TOKEN')


# Запуск планировщика внутри функции main
async def main():
    bot = Bot(
        token=TELEGRAM_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.include_routers(
        start.router,
        yandex.router,
        data_edit.router,
        insigth.router
    )

    # Настройка планировщика
    scheduler = BackgroundScheduler()

    # Ежечасная задача
    scheduler.add_job(
        func=asyncio.ensure_future(send_result_hour_task(bot)),
        trigger='interval',
        hours=1
    )

    # Ежедневная задача
    scheduler.add_job(
        func=asyncio.ensure_future(send_result_day_task(bot)),
        trigger='interval',
        days=1
    )

    # Ежемесячная задача
    scheduler.add_job(
        func=asyncio.ensure_future(send_result_month_task(bot)),
        trigger='cron',
        day=10,
        hour=5,
        minute=0
    )

    # Запуск планировщика
    scheduler.start()

    # Запуск фоновой задачи для проверки новых отзывов
    periodic_task = asyncio.create_task(
        periodically_tasks.check_new_reviews_periodically(bot)
    )

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
        # Дожидаемся завершения фоновой задачи
        await periodic_task
    except Exception as error:
        logging.error(f"Произошла ошибка: {error}")
    finally:
        if scheduler.running:
            scheduler.shutdown()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
    )
    asyncio.run(main())
