from os import getenv
from dotenv import load_dotenv
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Загрузка переменных окружения из .env файла
load_dotenv()

# Формируем строку подключения к базе данных PostgreSQL
DATA_URL = (
    f"postgresql://{getenv('DB_USER')}:{getenv('DB_PASSWORD')}@"
    f"{getenv('DB_HOST')}:{getenv('DB_PORT')}/{getenv('DB_NAME')}"
)

# Логируем строку подключения
logging.info(f"Подключение к базе данных: {DATA_URL}")

# Настройка SQLAlchemy
Base = declarative_base()

try:
    # Попытка создать соединение с базой данных
    engine = create_engine(DATA_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    logging.info("Подключение к базе данных установлено успешно.")
except Exception as e:
    # Логируем ошибку подключения, если она произошла
    logging.error(f"Ошибка подключения к базе данных: {e}")
    exit(1)


def create_tables():
    """Функция для создания всех таблиц в базе данных."""
    try:
        # Создание всех таблиц, если они еще не существуют
        Base.metadata.create_all(engine)
        logging.info("Таблицы созданы успешно!")
    except Exception as e:
        # Логируем ошибку создания таблиц, если она произошла
        logging.error(f"Ошибка создания таблиц: {e}")
        exit(1)
