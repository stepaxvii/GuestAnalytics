from sqlalchemy import (
    create_engine,
    Boolean,
    Column,
    Date,
    Integer,
    ForeignKey,
    SmallInteger,
    String,
    Text
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


# Настраиваем базу данных
DATA_URL = "sqlite:///guestanal.db"
Base = declarative_base()
engine = create_engine(DATA_URL)
Session = sessionmaker(bind=engine)

Session()
session = Session()


class Company(Base):
    """Модель компании."""

    __talename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    country = Column(String(255), nullable=True)
    manager_contact = Column(Integer, nullable=True)
    email = Column(String(255), nullable=False)


class Restaurant(Base):
    """Модель ресторана."""

    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    title = Column(String(255), nullable=False)
    rest_link = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    subs = Column(Boolean, nullable=False)
    manager_name = Column(String(255), nullable=False)
    manager_contact = Column(Integer, nullable=True)
    email = Column(String(255), nullable=False)

    company = relationship("Company", back_populates="restaurants")


class YandexReview(Base):
    """Модель отзыва Яндекса."""

    __tablename__ = "yandex_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    created_at = Column(Date, nullable=False)
    author = Column(String(255), nullable=False)
    rating = Column(SmallInteger, nullable=False)
    content = Column(Text, nullable=False)
    semantic = Column(String(255), nullable=True)

    restarant = relationship("Restaurant", back_populates="yandex_reviews")


class TwogisReview(Base):
    """Модель отзыва 2ГИС."""

    __tablename__ = "twogis_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    created_at = Column(Date, nullable=False)
    author = Column(String(255), nullable=False)
    rating = Column(SmallInteger, nullable=False)
    content = Column(Text, nullable=False)
    semantic = Column(String(255), nullable=True)

    restarant = relationship("Restaurant", back_populates="twogis_reviews")


# Обратные связи моделей.
Company.restaurants = relationship(
    "Restaurant", order_by=Restaurant.id, back_populates="company")
Restaurant.yandex_reviews = relationship(
    "YandexReview", order_by=YandexReview.id, back_populates="restaurant")
Restaurant.twogis_reviews = relationship(
    "TwogisReview", order_by=TwogisReview.id, back_populates="restaurant")


# Создаём таблицы
Base.metadata.create_all(engine)
