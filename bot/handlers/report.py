import asyncio
import io
import logging

from aiogram import Router, Bot
from aiogram.types import (
    BufferedInputFile,
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
    generate_combined_donut_report_bytes,
    get_count_reviews,
    get_previous_month
)
load_dotenv()

router = Router()


# Настройка логирования
logger = logging.getLogger()


async def send_monthly_report(bot: Bot):
    """Отправка автоматического ежемесячного отчёта в телеграм."""
    report_date = get_previous_month()
    year, month = report_date.split('-')
    month_name = month_dict.get(month, "предыдущий месяц")
    report_date = f"{month_name} {year}"

    restaurants = read_all_restaurant_data()
    for restaurant in restaurants:
        rest_id = restaurant['id']
        rest_wp_id = restaurant['wp_id']
        rest_title = restaurant['title']
        rest_address = restaurant['address']
        rest_tg_channal = restaurant['tg_channal']

        dashoard_link = (
            "https://guestanalytics.ru/"
            f"my-account/?dashboard={rest_wp_id}"
        )
        total, twogis, yandex = get_count_reviews(restaurant_id=rest_id)
        avg_total, avg_twogis, avg_yandex = avg_rest_rating(
            restaurant_id=rest_id
        )
        overall_nps, twogis_nps, yandex_nps = calculate_nps(
            restaurant_id=rest_id
        )
        (
            overall_satisfaction,
            twogis_satisfaction,
            yandex_satisfaction
        ) = calculate_satisfaction_level(restaurant_id=rest_id)
        insights = read_rest_month_insight_list(restaurant_id=rest_id)
        rating_count = count_reviews_by_rating(restaurant_id=rest_id)
        sorted_ratings = sorted(rating_count.items(), reverse=True)

        insights_text = "\n".join(f"📌{insight}." for insight in insights)
        rating_text = "\n".join(
            f"{star_for_report(rating)} - {count}" for rating,
            count in sorted_ratings
        )

        data = {
            'reviews': {
                '2ГИС': twogis,
                'Яндекс': yandex,
                'Все': total
            },
            'rating': {
                '2ГИС': avg_twogis,
                'Яндекс': avg_yandex,
                'Все': avg_total
            },
            'nps': {
                '2ГИС': twogis_nps,
                'Яндекс': yandex_nps,
                'Все': overall_nps
            },
            'satisfaction': {
                '2ГИС': twogis_satisfaction,
                'Яндекс': yandex_satisfaction,
                'Все': overall_satisfaction
            }
        }

        caption = (
            f"📈Отчёт за {report_date}\n"
            f"<b>{rest_title}, {rest_address}</b>.\n\n"
            f"📊 <b>Отзывы по рейтингу:</b>\n{rating_text}\n\n"
            f"<b>Обновлённые инсайты</b>:\n{insights_text[:300]}..."
            "[подробнее по кнопке внизу]"
        )

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
            f"📊 <b>Отзывы по рейтингу:</b>\n{rating_text}\n\n"
            f"<b>Обновлённые инсайты</b>:\n{insights_text[:300]}..."
            "[побробнее по кнопке внизу]"
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text="💻 Полная статистика",
                    url=dashoard_link
                )]
            ]
        )

        try:
            image_bytes = generate_combined_donut_report_bytes(
                data,
                rest_title,
                rest_address,
                report_date
            )
            if image_bytes:
                image_io = io.BytesIO(image_bytes)
                image_io.name = f"{rest_title}_report.png"
                image_io.seek(0)
                photo = BufferedInputFile(
                    image_io.read(),
                    filename=image_io.name
                )

                await bot.send_photo(
                    chat_id=rest_tg_channal,
                    photo=photo,
                    caption=caption,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            else:
                raise ValueError(
                    "Не удалось сгенерировать изображение."
                )
        except Exception as e:
            logger.warning(f"Ошибка генерации отчёта для {rest_title}: {e}")
            await bot.send_message(
                chat_id=rest_tg_channal,
                text=message,
                reply_markup=keyboard,
                parse_mode="HTML"
            )

        logger.info(f"Отчёт для ресторана {rest_title} отправлен.")
        await asyncio.sleep(3)
