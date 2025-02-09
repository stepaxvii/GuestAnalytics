import asyncio
import logging
import sys
from multiprocessing import Process

from bot.bot_main import main as start_bot
from api.app import start_flask

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
)


def main():
    # Запуск Flask сервера в отдельном процессе
    flask_process = Process(target=start_flask)
    flask_process.start()

    # Запуск бота в основном потоке с использованием asyncio
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    finally:
        # Остановка Flask процесса при завершении бота
        flask_process.terminate()
        flask_process.join()


if __name__ == "__main__":
    main()
