import openai
from os import getenv
import time

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    raise ValueError("API Key не инициализирован!")


def month_insight(reviews_block):
    "Определение семантического настроения отдельного отзыва."

    openai.api_key = OPENAI_API_KEY

    prompt = (
        f"""Ты — профессиональный аналитик ресторанного бизнеса и эксперт по обработке клиентских отзывов.
        Тебе дан массив отзывов гостей. Твоя задача — выявить 5–15 ключевых инсайтов,
        которые помогут владельцу ресторана улучшить сервис.

        Что считать инсайтом:
        - Проблема или тренд, который повторяется у нескольких гостей.
        - Положительный аспект, который ценят клиенты и стоит развивать.
        - Конкретные рекомендации владельцу на основе анализа.

        Чего НЕ ДЕЛАТЬ:
        - НЕ цитируй отзывы напрямую.
        - НЕ используй общие фразы типа "вкусная барабулька" или "уютная атмосфера".
        - НЕ дублируй одно и то же разными словами.
        - НЕ выдавай инсайты, если их нет — в этом случае просто напиши "Нет значимых инсайтов".

        Формат ответа:
        - Только четкие, осмысленные инсайты без вводных слов.
        - Каждый инсайт — отдельной строкой, без номеров и маркеров.
        - Отвечай строго по делу, без пояснений, JSON-структур и лишнего текста.

        Анализируй и выдавай инсайты для следующих отзывов:
        "{reviews_block}" """
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7
        )
        return response['choices'][0]['message']['content']

    except openai.error.APIError as e:
        print(f"OpenAI API ошибка: {e}")
        time.sleep(5)
        return month_insight(reviews_block)
