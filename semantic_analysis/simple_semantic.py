import openai

from os import getenv
from dotenv import load_dotenv

load_dotenv()

OPEN_AI_API_KEY = getenv('OPEN_AI_API_KEY', default='')


def simple_semantic(review_text):
    "Определение семантического настроения отдельного отзыва."

    openai.api_key = OPEN_AI_API_KEY

    # Промпт для OpenAI
    prompt = f"""Вы профессионал по анализу отзывов клиентов ресторана.
    Проведите семантический анализ и оцените, является ли следующий отзыв
     положительным (П), отрицательным (О) или нейтральным (Н).
    Верните только одну из следующих букв: "П", "О", "Н".
    Вот текст отзыва:

    Отзыв: "{review_text}"

    Ваш ответ:"""

    # Запрос к OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=10,  # Ограничение на количество токенов
        temperature=0.7
    )
    return response['choices'][0]['message']['content']
