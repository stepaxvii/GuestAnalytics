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


# Основная функция для запуска Flask и бота
def main():
    # Запуск Flask сервера в отдельном процессе
    flask_process = Process(target=start_flask)
    flask_process.start()

    # Запуск бота в основном потоке с использованием asyncio
    asyncio.run(start_bot())

    # Ждем завершения процесса Flask
    flask_process.join()


# Запуск
if __name__ == "__main__":
    main()
