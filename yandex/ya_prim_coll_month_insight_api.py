import logging
import sys

from data.create_data import create_insight
from data.read_data import read_rest_ya_reviews_date
from semantic_analysis.month_insight import month_insight
from utils.date import month_for_prim_coll
from utils.semantic import make_count_insights


# Настройка логирования
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


def primary_month_insight(rest_id: int):
    """Функция первичного сбора месячных инсайтов."""

    logger.info(
        f"Запускаем первичный анализ инсайтов для ресторана {rest_id}."
    )
    try:
        date_list = month_for_prim_coll()
        logger.info(
            f"Найдено {len(date_list)} уникальных дат для ресторана {rest_id}."
        )
    except Exception as e:
        logger.error(f"Ошибка при получении дат для ресторана {rest_id}: {e}")
        return  # Если не удается получить даты, завершить функцию

    for date in date_list:
        try:
            # Извлекаем отзывы за месяц
            reviews_data = read_rest_ya_reviews_date(
                restaurant_id=rest_id, date_filter=date
            )

            # Запрашиваем инсайты от openAI
            count_insights = make_count_insights(review_block=reviews_data)
            logger.info(
                f"Отправляю на анализ {len(reviews_data)} отзывов за {date}."
            )
            insight = month_insight(
                reviews_block=reviews_data, count_insights=count_insights
            )

            # Сохраняем инсайты в БД
            if insight:
                try:
                    insight_data = (rest_id, date, insight)
                    create_insight(data=insight_data)
                    logger.info(f"Инсайт для {date} успешно сохранен.")
                except Exception as e:
                    logger.error(
                        f"Ошибка при сохранении инсайтов для {date}: {e}"
                    )
        except Exception as e:
            logger.error(
                f"Ошибка при обработке отзывов за {date} для id {rest_id}: {e}"
            )
