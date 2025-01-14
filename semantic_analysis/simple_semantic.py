import openai
from os import getenv
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    raise ValueError("API Key is missing!")


def simple_semantic(review_text):
    "Определение семантического настроения отдельного отзыва."

    openai.api_key = OPENAI_API_KEY  # Убедитесь, что ключ передан

    prompt = f"""Вы профессионал по анализу отзывов клиентов ресторана.
    Проведите семантический анализ и оцените, является ли следующий отзыв
     положительным (П), отрицательным (О) или нейтральным (Н).
    Верните только одну из следующих букв: "П", "О", "Н".
    Вот текст отзыва:

    Отзыв: "{review_text}"

    Ваш ответ:"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10,
        temperature=0.7
    )

    return response['choices'][0]['message']['content']
