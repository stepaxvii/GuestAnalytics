import asyncio
import logging
from os import getenv

from aiogram import Router, Bot
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from dotenv import load_dotenv

from data.read_data import (
    read_all_restaurant_data,
    read_rest_month_insight_list
)
from utils.date import month_dict
from utils.message_text import star_for_report
from utils.monthly_report_tg import (
    avg_rest_rating,
    calculate_nps,
    calculate_satisfaction_level,
    count_reviews_by_rating,
    get_count_reviews,
    get_previous_month
)
load_dotenv()

router = Router()

ADMIN_ID = int(getenv('ADMIN_ID'))

# Настройка логирования
logger = logging.getLogger()


async def check_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь администратором."""
    return user_id == ADMIN_ID


@router.callback_query(lambda c: c.data == 'test_report')
async def test_report(callback_query: CallbackQuery, bot: Bot):
    """Тестируем работу ежемесячного отчёта."""

    if await check_admin(callback_query.from_user.id):
        await callback_query.answer(
            text="Запускаю тест месячного отчёта"
        )

        # Получаем отчётный месяц
        report_date = get_previous_month()
        year, month = report_date.split('-')
        month_name = month_dict.get(month, "предыдущий месяц")
        report_date = f"{month_name} {year}"

        # Получаем данные о ресторанах
        restaurants = read_all_restaurant_data()
        for restaurant in restaurants:
            rest_id = restaurant['id']
            rest_wp_id = restaurant['wp_id']
            rest_title = restaurant['title']
            rest_address = restaurant['address']
            rest_tg_channal = -1002453477756
            # Формируем ссылку на dashboard
            dashoard_link = (
                "https://guestanalytics.ru/"
                f"my-account/?dashboard={rest_wp_id}"
            )
            # Количество отзывов
            total, twogis, yandex = get_count_reviews(restaurant_id=rest_id)

            # Средний рейтинг
            avg_total, avg_twogis, avg_yandex = avg_rest_rating(
                restaurant_id=rest_id
            )

            # Лояльность гостей
            overall_nps, twogis_nps, yandex_nps = calculate_nps(
                restaurant_id=rest_id
            )

            # Настроение гостей
            (
                overall_satisfaction,
                twogis_satisfaction,
                yandex_satisfaction
            ) = calculate_satisfaction_level(restaurant_id=rest_id)

            # Запрашиваем инсайты
            insights = read_rest_month_insight_list(restaurant_id=rest_id)
            # Подсчитываем количество отзывов с разным рейтингом
            rating_count = count_reviews_by_rating(restaurant_id=rest_id)

            # Сортируем по ключам (рейтингам) от 1 до 5
            sorted_ratings = sorted(rating_count.items(), reverse=True)

            # Добавляем информацию об инсайтах
            insights_text = ""
            for insight in insights:
                insights_text += f"- {insight}"
            # Добавляем информацию о каждом рейтинге в сообщение
            rating_text = ""
            for rating, count in sorted_ratings:
                rating_text += f"{star_for_report(rating)} - {count}\n"

            logger.info(f"Отчёт для ресторана {rest_title} готов!")

            # Формируем сообщение для отправки в телеграм
            message = (
                f"📈Отчёт за {report_date}\n"
                f"<b>{rest_title}, {rest_address}</b>.\n\n"
                f"📝 <b>Общее количество</b>: {total}\n"
                f"Яндекс: {yandex}\n"
                f"2ГИС: {twogis}\n\n"
                f"🏆 <b>Индекс лояльности (NPS)</b>: {overall_nps}%\n"
                f"Яндекс: {yandex_nps}%\n"
                f"2ГИС: {twogis_nps}%\n\n"
                f"⭐ <b>Средний рейтинг</b>: {avg_total}\n"
                f"Яндекс: {avg_yandex}\n"
                f"2ГИС: {avg_twogis}\n\n"
                f"😊 <b>Положительная семантика</b>: {overall_satisfaction}%\n"
                f"Яндекс: {yandex_satisfaction}%\n"
                f"2ГИС: {twogis_satisfaction}%\n\n"
            )

            # Добавляем количество отзывов на каждый рейтинг
            message += (
                f"📊 <b>Отзывы по рейтингу:</b>\n{rating_text}\n"
            )
            # Добавляем к отчёту первый инсайт
            message += f"Обновлённые инсайты:\n{insights_text[:300]}..."

            # Создаем кнопку с ссылкой
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text="💻 Полная статистика", url=dashoard_link
                    )]
                ]
            )

            await callback_query.bot.send_message(
                chat_id=rest_tg_channal,
                text=message,
                reply_markup=keyboard
            )
            logger.info(f"Отчёт для ресторана {rest_title} отправлен!")
            await asyncio.sleep(3)

        logger.info("Тест отчёта завершён)")
