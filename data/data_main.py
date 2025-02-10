from os import getenv
from dotenv import load_dotenv

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    ForeignKey,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from constants import MAX_LENGTH_STR

load_dotenv()

# Настройка подключения к PostgreSQL
DATA_URL = (
    f"postgresql://{getenv('DB_USER')}:{getenv('DB_PASSWORD')}@"
    f"{getenv('DB_HOST')}:{getenv('DB_PORT')}/{getenv('DB_NAME')}"
)

Base = declarative_base()
engine = create_engine(DATA_URL)
Session = sessionmaker(bind=engine)
session = Session()


class Restaurant(Base):
    """Модель ресторана."""

    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True)
    title = Column(String(MAX_LENGTH_STR), nullable=False)
    yandex_link = Column(String(MAX_LENGTH_STR), nullable=False, unique=True)
    twogis_link = Column(String(MAX_LENGTH_STR), unique=True)
    address = Column(Text, nullable=False)
    tg_channal = Column(String(MAX_LENGTH_STR))


class YandexReview(Base):
    """Модель отзыва Яндекса."""

    __tablename__ = "yandex_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    restaurant_id = Column(
        Integer, ForeignKey("restaurants.id"), nullable=False
    )
    created_at = Column(String(MAX_LENGTH_STR), nullable=False)
    author = Column(String(MAX_LENGTH_STR), nullable=False)
    link = Column(String(MAX_LENGTH_STR))
    rating = Column(SmallInteger, nullable=False)
    content = Column(Text, nullable=False)
    semantic = Column(String(MAX_LENGTH_STR))

    restaurant = relationship("Restaurant", back_populates="yandex_reviews")


class TwogisReview(Base):
    """Модель отзыва 2ГИС."""

    __tablename__ = "twogis_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    restaurant_id = Column(
        Integer, ForeignKey("restaurants.id"), nullable=False
    )
    created_at = Column(String(MAX_LENGTH_STR), nullable=False)
    author = Column(String(MAX_LENGTH_STR), nullable=False)
    link = Column(String(MAX_LENGTH_STR))
    rating = Column(SmallInteger, nullable=False)
    content = Column(Text, nullable=False)
    semantic = Column(String(MAX_LENGTH_STR))

    restaurant = relationship("Restaurant", back_populates="twogis_reviews")


# Обратные связи моделей
Restaurant.yandex_reviews = relationship(
    "YandexReview", order_by=YandexReview.id, back_populates="restaurant"
)
Restaurant.twogis_reviews = relationship(
    "TwogisReview", order_by=TwogisReview.id, back_populates="restaurant"
)

# Создаём таблицы
Base.metadata.create_all(engine)
