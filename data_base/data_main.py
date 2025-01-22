from sqlalchemy import (
    create_engine,
    Boolean,
    Column,
    Integer,
    ForeignKey,
    SmallInteger,
    String,
    Text
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from constants import MAX_LENGTH_STR


# Настраиваем базу данных
DATA_URL = "sqlite:///guestanal.db"
Base = declarative_base()
engine = create_engine(DATA_URL)
Session = sessionmaker(bind=engine)

Session()
session = Session()


class Company(Base):
    """Модель компании."""

    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(MAX_LENGTH_STR), nullable=False)
    country = Column(String(MAX_LENGTH_STR), nullable=True)
    manager_name = Column(String(MAX_LENGTH_STR), nullable=False)
    manager_contact = Column(Integer, nullable=True)
    email = Column(String(MAX_LENGTH_STR), nullable=False)


class Restaurant(Base):
    """Модель ресторана."""

    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    title = Column(String(MAX_LENGTH_STR), nullable=False)
    yandex_link = Column(String(MAX_LENGTH_STR), nullable=False, unique=True)
    twogis_link = Column(String(MAX_LENGTH_STR), nullable=True, unique=True)
    address = Column(Text, nullable=False)
    subs = Column(Boolean, nullable=True)  # Времено
    manager_name = Column(String(MAX_LENGTH_STR), nullable=True)  # Времено
    manager_contact = Column(Integer, nullable=True)  # Времено
    tg_channal = Column(String(MAX_LENGTH_STR), nullable=True)  # Времено
    email = Column(String(MAX_LENGTH_STR), nullable=True)  # Времено

    company = relationship("Company", back_populates="restaurants")


class YandexReview(Base):
    """Модель отзыва Яндекса."""

    __tablename__ = "yandex_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False
    )
    created_at = Column(String(MAX_LENGTH_STR), nullable=False)
    author = Column(String(MAX_LENGTH_STR), nullable=False)
    link = Column(String(MAX_LENGTH_STR), nullable=True)
    rating = Column(SmallInteger, nullable=False)
    content = Column(Text, nullable=False)
    semantic = Column(String(MAX_LENGTH_STR), nullable=True)

    restaurant = relationship("Restaurant", back_populates="yandex_reviews")


class TwogisReview(Base):
    """Модель отзыва 2ГИС."""

    __tablename__ = "twogis_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False
    )
    created_at = Column(String(MAX_LENGTH_STR), nullable=False)
    author = Column(String(MAX_LENGTH_STR), nullable=False)
    link = Column(String(MAX_LENGTH_STR), nullable=True)
    rating = Column(SmallInteger, nullable=False)
    content = Column(Text, nullable=False)
    semantic = Column(String(MAX_LENGTH_STR), nullable=True)

    restaurant = relationship("Restaurant", back_populates="twogis_reviews")


# Обратные связи моделей
Company.restaurants = relationship(
    "Restaurant", order_by=Restaurant.id, back_populates="company")
Restaurant.yandex_reviews = relationship(
    "YandexReview", order_by=YandexReview.id, back_populates="restaurant")
Restaurant.twogis_reviews = relationship(
    "TwogisReview", order_by=TwogisReview.id, back_populates="restaurant")


# Создаём таблицы
Base.metadata.create_all(engine)
