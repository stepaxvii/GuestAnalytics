import logging

from api.db import session
from data.create_data import create_insight
from data.read_data import get_unique_sorted_dates, read_rest_ya_reviews_date
from semantic_analysis.month_insight import month_insight


# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def primary_month_insight(rest_id: int):
    """Функция первичного сбора месячных инсайтов."""

    logger.info(
        f"Запускаем первичный анализ инсайтов для ресторана {rest_id}."
    )
    try:
        date_list = get_unique_sorted_dates(session=session, rest_id=rest_id)
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
            logger.info(
                f"Отправляю на анализ {len(reviews_data)} отзывов за {date}."
            )
            insight = month_insight(reviews_block=reviews_data)

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
