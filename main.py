import asyncio
import logging
import sys
import threading

from bot.bot_main import main as start_bot
from api.app import start_flask

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
)


async def main():
    # Запуск Flask сервера в отдельном потоке
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.start()

    # Запуск бота в основном потоке
    await start_bot()


# Запуск
if __name__ == "__main__":
    asyncio.run(main())
