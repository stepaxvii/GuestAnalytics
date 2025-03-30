import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from bot import periodically_tasks
from bot.handlers import insight, start, yandex, data_edit

load_dotenv()

# Из окружения извлекаем необходимые токены, ключи и переменные
TELEGRAM_TOKEN = getenv('TELEGRAM_TOKEN')

# Настройка логирования
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Создаем обработчик для вывода логов в консоль
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Форматирование логов
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
console_handler.setFormatter(formatter)

# Добавляем обработчик к логгеру
logger.addHandler(console_handler)


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
        insight.router
    )

    # Запуск фоновой задачи для проверки новых отзывов
    check_twogis = asyncio.create_task(
        periodically_tasks.check_twogis_new_reviews_periodically
    )
    check_yandex = asyncio.create_task(
        periodically_tasks.check_ya_new_reviews_periodically(bot)
    )
    check_insight = asyncio.create_task(
        periodically_tasks.check_new_insight_periodically(bot)
    )

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
        # Дожидаемся завершения фоновых задач
        await check_twogis
        await check_yandex
        await check_insight
    except Exception as error:
        logger.error(f"Произошла ошибка: {error}")


if __name__ == "__main__":
    logger.info("Запуск bot_app!")
    asyncio.run(main())
