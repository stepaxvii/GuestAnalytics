from os import getenv
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

DATA_URL = (
    f"postgresql://{getenv('DB_USER')}:{getenv('DB_PASSWORD')}@"
    f"{getenv('DB_HOST')}:{getenv('DB_PORT')}/{getenv('DB_NAME')}"
)

# Настройка SQLAlchemy
Base = declarative_base()
engine = create_engine(DATA_URL)
Session = sessionmaker(bind=engine)
session = Session()


def create_tables():
    """Функция для создания всех таблиц."""
    Base.metadata.create_all(engine)
