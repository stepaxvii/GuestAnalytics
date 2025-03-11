import openai
from os import getenv
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    raise ValueError("API Key is missing!")


def month_insight(reviews_block):
    "Определение семантического настроения отдельного отзыва."

    openai.api_key = OPENAI_API_KEY

    prompt = (
        f"""Ты — продвинутый эксперт по анализу отзывов о ресторанах.
        Тебе дан блок текстов. Твоя задача — извлечь из них 5–15 чётких и
         конкретных инсайтов для владельца ресторана.
        Твои основные правила:
        1. Никаких пояснений, вводных слов, рассуждений или заключений.
        2. Каждый инсайт — в отдельной строке. Без номеров, тире, звёздочек,
         маркеров и т.п.
        3. Только 10 важнейших строк-инсайтов. Ни больше, ни меньше.
        4. Запрещено возвращать любое дополнительное сопровождение,
         рекомендации, выводы, структуру JSON, кавычки и пр.
        Исключительно строки с инсайтами.
        5. Нумеровать инсайты также запрещено.

        Обработай следующие отзывы и выдай свои инсайты:
        "{reviews_block}" """
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.7
    )

    return response['choices'][0]['message']['content']
