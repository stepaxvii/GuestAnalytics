# import asyncio
# import logging
# import sys
# from os import getenv

# from aiogram import Bot, Dispatcher
# from aiogram.client.default import DefaultBotProperties
# from aiogram.enums import ParseMode
# from dotenv import load_dotenv

# from bot import periodically_tasks
# from bot.handlers import insight, start, yandex, data_edit

# load_dotenv()

# # Из окружения извлекаем необходимые токены, ключи и переменные
# TELEGRAM_TOKEN = getenv('TELEGRAM_TOKEN')


# # Запуск планировщика внутри функции main
# async def main():
#     bot = Bot(
#         token=TELEGRAM_TOKEN,
#         default=DefaultBotProperties(parse_mode=ParseMode.HTML)
#     )
#     dp = Dispatcher()
#     dp.include_routers(
#         start.router,
#         yandex.router,
#         data_edit.router,
#         insight.router
#     )

#     # Запуск фоновой задачи для проверки новых отзывов
#     periodic_task = asyncio.create_task(
#         periodically_tasks.check_new_reviews_periodically(bot)
#     )
#     another_periodic_task = asyncio.create_task(
#         periodically_tasks.check_new_insight_periodically(bot)
#     )

#     try:
#         await bot.delete_webhook(drop_pending_updates=True)
#         await dp.start_polling(bot)
#         # Дожидаемся завершения фоновых задач
#         await periodic_task
#         await another_periodic_task
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
logging.basicConfig(
    level=logging.INFO,  # Устанавливаем уровень логирования INFO
    stream=sys.stdout,    # Выводим логи в стандартный вывод
)


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
    periodic_task = asyncio.create_task(
        periodically_tasks.check_new_reviews_periodically(bot)
    )
    another_periodic_task = asyncio.create_task(
        periodically_tasks.check_new_insight_periodically(bot)
    )

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
        # Дожидаемся завершения фоновых задач
        await periodic_task
        await another_periodic_task
    except Exception as error:
        logging.error(f"Произошла ошибка: {error}")

if __name__ == "__main__":
    # Логирование в main, если нужно вывести дополнительные логи
    logging.info('Запуск Telegram-бота...')
    asyncio.run(main())
