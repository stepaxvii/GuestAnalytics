
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    ForeignKey,
    SmallInteger,
    String,
    Text
)
from sqlalchemy.orm import relationship
from api.db import Base


class Restaurant(Base):
    """Модель ресторана."""
    __tablename__ = "restaurants"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    yandex_link = Column(String(255), nullable=False, unique=True)
    twogis_link = Column(String(255), unique=True)
    address = Column(Text, nullable=False)
    tg_channal = Column(String(255))
    subscription = Column(Boolean, default=True)


class YandexReview(Base):
    """Модель отзыва Яндекса."""
    __tablename__ = "yandex_reviews"
    id = Column(Integer, primary_key=True, autoincrement=True)
    restaurant_id = Column(
        Integer, ForeignKey("restaurants.id"), nullable=False
    )
    created_at = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    link = Column(String(255))
    rating = Column(SmallInteger, nullable=False)
    content = Column(Text, nullable=False)
    semantic = Column(String(255))
    restaurant = relationship("Restaurant", back_populates="yandex_reviews")


class TwogisReview(Base):
    """Модель отзыва 2ГИС."""
    __tablename__ = "twogis_reviews"
    id = Column(Integer, primary_key=True, autoincrement=True)
    restaurant_id = Column(
        Integer, ForeignKey("restaurants.id"), nullable=False
    )
    created_at = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    link = Column(String(255))
    rating = Column(SmallInteger, nullable=False)
    content = Column(Text, nullable=False)
    semantic = Column(String(255))
    restaurant = relationship("Restaurant", back_populates="twogis_reviews")


# Обратные связи моделей
Restaurant.yandex_reviews = relationship(
    "YandexReview", order_by=YandexReview.id, back_populates="restaurant"
)
Restaurant.twogis_reviews = relationship(
    "TwogisReview", order_by=TwogisReview.id, back_populates="restaurant"
)
