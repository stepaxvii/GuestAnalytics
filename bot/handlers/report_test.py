import asyncio
import io
import math
import logging
from aiogram import Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.types import BufferedInputFile
from dotenv import load_dotenv
import matplotlib.pyplot as plt

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

logger = logging.getLogger()
router = Router()


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
    fig.suptitle(f"{restaurant_name} | {restaurant_address}", fontsize=32, fontweight='bold', y=0.95)

    has_valid_data = False  # Будет True, если хотя бы один график построен

    for ax, metric, title in zip(axs.flat, metrics, titles):
        values = data.get(metric, {})
        center_val = values.get("Все")
        if center_val is None:
            ax.text(0.5, 0.5, "Нет данных", ha='center', va='center', fontsize=20, color='red')
            ax.set_title(title, fontsize=26, fontweight='bold', pad=15)
            ax.axis('off')
            continue

        platforms = [k for k in values.keys() if k != "Все"]
        numbers = [values[k] for k in platforms]

        if not numbers or any(x is None or np.isnan(x) for x in numbers):
            ax.text(0.5, 0.5, "Нет данных", ha='center', va='center', fontsize=20, color='red')
            ax.set_title(title, fontsize=26, fontweight='bold', pad=15)
            ax.axis('off')
            continue

        has_valid_data = True  # Хотя бы один валидный

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

        ax.text(0, 0, center_text, ha='center', va='center', fontsize=32, fontweight='bold')
        ax.set_title(title, fontsize=26, fontweight='bold', pad=15)
        ax.set_aspect('equal')
        ax.axis('off')

    if not has_valid_data:
        plt.close(fig)
        return None  # Ничего не строилось

    plt.subplots_adjust(hspace=0.35, wspace=0.4, bottom=0.1, top=0.85)
    fig.text(0.1, 0.04, report_date, fontsize=24, fontweight='medium', ha='left', va='center')
    fig.text(0.9, 0.04, "подготовлено GuestAnalytics", fontsize=24, fontweight='medium', ha='right', va='center')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300)
    plt.close(fig)
    buf.seek(0)
    return buf.read()


@router.callback_query(lambda c: c.data == 'test_report')
async def send_monthly_report(callback_query: CallbackQuery):
    bot = callback_query.bot
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
        rest_tg_channal = '-1002453477756'

        dashoard_link = (
            "https://guestanalytics.ru/"
            f"my-account/?dashboard={rest_wp_id}"
        )

        total, twogis, yandex = get_count_reviews(restaurant_id=rest_id)
        avg_total, avg_twogis, avg_yandex = avg_rest_rating(restaurant_id=rest_id)
        overall_nps, twogis_nps, yandex_nps = calculate_nps(restaurant_id=rest_id)
        overall_satisfaction, twogis_satisfaction, yandex_satisfaction = calculate_satisfaction_level(restaurant_id=rest_id)
        insights = read_rest_month_insight_list(restaurant_id=rest_id)
        rating_count = count_reviews_by_rating(restaurant_id=rest_id)
        sorted_ratings = sorted(rating_count.items(), reverse=True)

        data = {
            'reviews': {'2ГИС': twogis, 'Яндекс': yandex, 'Все': total},
            'rating': {'2ГИС': avg_twogis, 'Яндекс': avg_yandex, 'Все': avg_total},
            'nps': {'2ГИС': twogis_nps, 'Яндекс': yandex_nps, 'Все': overall_nps},
            'satisfaction': {'2ГИС': twogis_satisfaction, 'Яндекс': yandex_satisfaction, 'Все': overall_satisfaction}
        }

        insights_text = "\n".join(f"📌{insight}." for insight in insights)
        rating_text = "\n".join(f"{star_for_report(rating)} ({count})" for rating, count in sorted_ratings)

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
                [InlineKeyboardButton(text="💻 Полная статистика", url=dashoard_link)]
            ]
        )

        try:
            image_bytes = generate_combined_donut_report_bytes(data, rest_title, rest_address, report_date)
            if image_bytes:
                image_io = io.BytesIO(image_bytes)
                image_io.name = f"{rest_title}_report.png"
                image_io.seek(0)
                photo = BufferedInputFile(image_io.read(), filename=image_io.name)

                await bot.send_photo(
                    chat_id=rest_tg_channal,
                    photo=photo,
                    caption=caption,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            else:
                raise ValueError("Не удалось сгенерировать изображение (нет валидных данных)")
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
