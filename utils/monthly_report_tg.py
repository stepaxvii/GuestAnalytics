import io
import math

from collections import Counter
from datetime import datetime
import matplotlib.pyplot as plt
from sqlalchemy import func

from api.db import session
from data.data_main import TwogisReview, YandexReview
from data.read_data import (
    read_rest_twogis_reviews_date,
    read_rest_ya_reviews_date
)
from utils.date import make_last_months


def generate_combined_donut_report_bytes(
        data: dict,
        restaurant_name: str,
        restaurant_address: str,
        report_date: str
) -> bytes | None:
    import numpy as np

    titles = [
        "Количество отзывов",
        "Средний рейтинг",
        "Индекс лояльности (NPS)",
        "Положительная семантика"
    ]
    metrics = ['reviews', 'rating', 'nps', 'satisfaction']
    colors = ['#4CAF50', '#F44336']

    fig, axs = plt.subplots(2, 2, figsize=(16, 16))
    fig.suptitle(
        f"{restaurant_name} | {restaurant_address}",
        fontsize=32, fontweight='bold',
        y=0.95
    )

    # Будет True, если хотя бы один график построен
    has_valid_data = False

    for ax, metric, title in zip(axs.flat, metrics, titles):
        values = data.get(metric, {})
        center_val = values.get("Все")
        if center_val is None:
            ax.text(
                0.5, 0.5, "Нет данных",
                ha='center',
                va='center',
                fontsize=20,
                color='red'
            )
            ax.set_title(title, fontsize=26, fontweight='bold', pad=15)
            ax.axis('off')
            continue

        platforms = [k for k in values.keys() if k != "Все"]
        numbers = [values[k] for k in platforms]

        if not numbers or any(x is None or np.isnan(x) for x in numbers):
            ax.text(
                0.5,
                0.5,
                "Нет данных",
                ha='center',
                va='center',
                fontsize=20,
                color='red'
            )
            ax.set_title(title, fontsize=26, fontweight='bold', pad=15)
            ax.axis('off')
            continue

        # Хотя бы один валидный
        has_valid_data = True

        wedges, _ = ax.pie(
            numbers,
            radius=1,
            colors=colors,
            startangle=90,
            wedgeprops=dict(width=0.6, edgecolor='white', linewidth=2)
        )

        for i, wedge in enumerate(wedges):
            ang = (wedge.theta2 + wedge.theta1) / 2
            x = 1.1 * math.cos(math.radians(ang))
            y = 1.1 * math.sin(math.radians(ang))
            if metric in ['nps', 'satisfaction']:
                label = f"{platforms[i]}: {numbers[i]:.0f}%"
            elif metric == 'reviews':
                label = f"{platforms[i]}: {int(numbers[i])}"
            else:
                label = f"{platforms[i]}: {numbers[i]:.1f}"
            ax.text(x, y, label, ha='center', va='center', fontsize=18,
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8))

        if metric == 'rating':
            center_text = f"{center_val:.2f}"
        elif metric in ['nps', 'satisfaction']:
            center_text = f"{center_val:.0f}%"
        else:
            center_text = f"{int(center_val)}"

        ax.text(
            0,
            0,
            center_text,
            ha='center',
            va='center',
            fontsize=32,
            fontweight='bold'
        )
        ax.set_title(title, fontsize=26, fontweight='bold', pad=15)
        ax.set_aspect('equal')
        ax.axis('off')

    if not has_valid_data:
        plt.close(fig)
        return None  # Ничего не строилось

    plt.subplots_adjust(hspace=0.35, wspace=0.4, bottom=0.1, top=0.85)
    fig.text(
        0.1,
        0.04,
        report_date,
        fontsize=24,
        fontweight='medium',
        ha='left',
        va='center'
    )
    fig.text(
        0.9,
        0.04,
        "подготовлено GuestAnalytics",
        fontsize=24,
        fontweight='medium',
        ha='right',
        va='center'
    )

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300)
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def get_previous_month():
    """Функция для определения предыдущего месяца."""

    # определяем текущую дату
    current_date = datetime.now()
    # Получаем предыдущий месяц
    previous_month = make_last_months(
        current_date=current_date
    )[0]

    return previous_month


def get_count_reviews(restaurant_id: int):
    """Функция определения количества отзывов за месяц."""

    previous_month = get_previous_month()
    # Получаем количество отзывов за искомый месяц
    yandex_reviews = len(read_rest_ya_reviews_date(
        restaurant_id=restaurant_id,
        date_filter=previous_month
    ))
    twogis_reviews = len(read_rest_twogis_reviews_date(
        restaurant_id=restaurant_id,
        date_filter=previous_month
    ))
    total_count_reviews = yandex_reviews + twogis_reviews

    return total_count_reviews, twogis_reviews, yandex_reviews


def avg_rest_rating(restaurant_id):
    """Получаем средний рейтинг отзывов с Яндекса и TwoGIS за прошлый месяц."""

    # Получаем предыдущий месяц
    previous_month = get_previous_month()

    # Получаем отзывы с Яндекса за предыдущий месяц
    yandex_reviews = read_rest_ya_reviews_date(
        restaurant_id=restaurant_id,
        date_filter=previous_month
    )

    # Получаем отзывы с TwoGIS за предыдущий месяц
    twogis_reviews = read_rest_twogis_reviews_date(
        restaurant_id=restaurant_id,
        date_filter=previous_month
    )

    # Если отзывы есть, рассчитываем средний рейтинг, иначе возвращаем 0
    if yandex_reviews:
        yandex_avg_rating = sum(
            [review.rating for review in yandex_reviews]
        ) / len(yandex_reviews)
    else:
        yandex_avg_rating = None

    if twogis_reviews:
        twogis_avg_rating = sum(
            [review.rating for review in twogis_reviews]
        ) / len(twogis_reviews)
    else:
        twogis_avg_rating = None

    # Если на одной из платформ есть отзывы, считаем рейтинг только по ней
    if yandex_avg_rating is not None and twogis_avg_rating is not None:
        average_rating = round((yandex_avg_rating + twogis_avg_rating) / 2, 1)
    elif yandex_avg_rating is not None:
        average_rating = round(yandex_avg_rating, 1)
    elif twogis_avg_rating is not None:
        average_rating = round(twogis_avg_rating, 1)
    else:
        average_rating = 0

    return (
        round(average_rating, 1),
        round((twogis_avg_rating if twogis_avg_rating is not None else 0), 1),
        round((yandex_avg_rating if yandex_avg_rating is not None else 0), 1)
    )


def count_reviews_by_rating(restaurant_id: int):
    """Подсчитываем количество отзывов с разным рейтингом."""
    # Получаем предыдущий месяц
    previous_month = get_previous_month()

    # Получаем отзывы с Яндекса за предыдущий месяц
    yandex_reviews = read_rest_ya_reviews_date(
        restaurant_id=restaurant_id,
        date_filter=previous_month
    )

    # Получаем отзывы с TwoGIS за предыдущий месяц
    twogis_reviews = read_rest_twogis_reviews_date(
        restaurant_id=restaurant_id,
        date_filter=previous_month
    )

    # Подсчитываем количество отзывов с каждым рейтингом на Яндексе
    if yandex_reviews:
        yandex_ratings = [review.rating for review in yandex_reviews]
        yandex_rating_count = dict(Counter(yandex_ratings))
    else:
        yandex_rating_count = {}

    # Подсчитываем количество отзывов с каждым рейтингом на TwoGIS
    if twogis_reviews:
        twogis_ratings = [review.rating for review in twogis_reviews]
        twogis_rating_count = dict(Counter(twogis_ratings))
    else:
        twogis_rating_count = {}

    # Сливаем результаты с двух платформ
    combined_rating_count = yandex_rating_count.copy()
    for rating, count in twogis_rating_count.items():
        combined_rating_count[
            rating
        ] = combined_rating_count.get(rating, 0) + count

    return combined_rating_count


def calculate_nps(restaurant_id):
    """Рассчитываем NPS за предыдущий месяц для Яндекса и TwoGIS."""
    try:
        # Получаем предыдущий месяц в формате YYYY-MM
        previous_month = get_previous_month()

        # Получаем количество отзывов с Яндекса за предыдущий месяц
        total_yandex_reviews = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            func.substr(YandexReview.created_at, 1, 7) == previous_month
        ).count()

        # Получаем количество отзывов с TwoGIS за предыдущий месяц
        total_twogis_reviews = session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id,
            func.substr(TwogisReview.created_at, 1, 7) == previous_month
        ).count()

        # Общее количество отзывов
        total_reviews = total_yandex_reviews + total_twogis_reviews

        if total_reviews == 0:
            return {
                'overall_nps': 0,
                'yandex_nps': 0,
                'twogis_nps': 0
            }

        # Яндекс: количество промотеров и детракторов за предыдущий месяц
        yandex_promoters = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            YandexReview.rating == 5,
            func.substr(YandexReview.created_at, 1, 7) == previous_month
        ).count()

        yandex_detractors = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            YandexReview.rating.in_([1, 2, 3]),
            func.substr(YandexReview.created_at, 1, 7) == previous_month
        ).count()

        if total_yandex_reviews > 0:
            yandex_nps = round(
                (
                    yandex_promoters - yandex_detractors
                ) / total_yandex_reviews * 100, 1)
        else:
            yandex_nps = 0

        # TwoGIS: количество промотеров и детракторов за предыдущий месяц
        twogis_promoters = session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id,
            TwogisReview.rating == 5,
            func.substr(TwogisReview.created_at, 1, 7) == previous_month
        ).count()

        twogis_detractors = session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id,
            TwogisReview.rating.in_([1, 2, 3]),
            func.substr(TwogisReview.created_at, 1, 7) == previous_month
        ).count()

        if total_twogis_reviews > 0:
            twogis_nps = round(
                (
                    twogis_promoters - twogis_detractors
                ) / total_twogis_reviews * 100, 1)
        else:
            twogis_nps = 0

        # Общий NPS за предыдущий месяц
        total_promoters = yandex_promoters + twogis_promoters
        total_detractors = yandex_detractors + twogis_detractors

        overall_nps = round(
            (total_promoters - total_detractors) / total_reviews * 100, 1)

        return overall_nps, twogis_nps, yandex_nps

    except Exception as e:
        session.rollback()
        raise e


def calculate_satisfaction_level(restaurant_id):
    """Рассчитываем уровень удовлетворенности за предыдущий месяц."""
    try:
        # Получаем предыдущий месяц
        previous_month = get_previous_month()

        # Получаем количество отзывов с Яндекса за предыдущий месяц
        total_yandex_reviews = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            func.substr(YandexReview.created_at, 1, 7) == previous_month
        ).count()

        # Получаем количество отзывов с TwoGIS за предыдущий месяц
        total_twogis_reviews = session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id,
            func.substr(TwogisReview.created_at, 1, 7) == previous_month
        ).count()

        total_reviews = total_yandex_reviews + total_twogis_reviews

        if total_reviews == 0:
            return {
                'overall_satisfaction': 0,
                'yandex_satisfaction': 0,
                'twogis_satisfaction': 0
            }

        # Положительные отзывы с Яндекса за предыдущий месяц
        yandex_positive = session.query(YandexReview).filter(
            YandexReview.restaurant_id == restaurant_id,
            YandexReview.semantic.ilike("п"),
            func.substr(YandexReview.created_at, 1, 7) == previous_month
        ).count()

        # Положительные отзывы с TwoGIS за предыдущий месяц
        twogis_positive = session.query(TwogisReview).filter(
            TwogisReview.restaurant_id == restaurant_id,
            TwogisReview.semantic.ilike("п"),
            func.substr(TwogisReview.created_at, 1, 7) == previous_month
        ).count()

        # Расчёты уровня удовлетворенности
        if total_yandex_reviews > 0:
            yandex_satisfaction = round(
                yandex_positive / total_yandex_reviews * 100, 1)
        else:
            yandex_satisfaction = 0

        if total_twogis_reviews > 0:
            twogis_satisfaction = round(
                twogis_positive / total_twogis_reviews * 100, 1)
        else:
            twogis_satisfaction = 0

        overall_satisfaction = round(
            (yandex_positive + twogis_positive) / total_reviews * 100, 1)

        return overall_satisfaction, twogis_satisfaction, yandex_satisfaction

    except Exception as e:
        session.rollback()
        raise e
