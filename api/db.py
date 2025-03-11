from os import getenv
from dotenv import load_dotenv
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

DATA_URL = (
    f"postgresql://{getenv('DB_USER')}:{getenv('DB_PASSWORD')}@"
    f"{getenv('DB_HOST')}:{getenv('DB_PORT')}/{getenv('DB_NAME')}"
)

logging.info(f"Connecting to: {DATA_URL}")

# Настройка SQLAlchemy
Base = declarative_base()
try:
    engine = create_engine(DATA_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
except Exception as e:
    logging.info(f"Ошибка подключения к базе данных: {e}")
    exit(1)


def create_tables():
    """Функция для создания всех таблиц."""
    try:
        Base.metadata.create_all(engine)
        logging.info("Таблицы созданы успешно!")
    except Exception as e:
        logging.info(f"Ошибка создания таблиц: {e}")
        exit(1)
