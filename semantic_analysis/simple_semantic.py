import time
from os import getenv

from dotenv import load_dotenv
import openai
import openai.error

load_dotenv()

OPENAI_API_KEY = getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    raise ValueError("API Key is missing!")


def simple_semantic(review_text):
    "Определение семантического настроения отдельного отзыва."

    openai.api_key = OPENAI_API_KEY

    prompt = (
        f"""Вы являетесь профессионалом по анализу отзывов клиентов ресторанов.
        Ваша задача — строго определить, является ли следующий отзыв
        положительным (П), отрицательным (О) или нейтральным (Н).
        Ответ должен содержать только одну из букв: "П", "О" или "Н".
        Никакие другие символы, слова, пояснения,
         пробелы или дополнительные тексты не допускаются.
        Верните только одну букву строго без кавычек, точек и прочих символов.

        Текст отзыва:
        "{review_text}" """
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0.7
        )
        return response['choices'][0]['message']['content']

    except openai.error.APIError as e:
        print(f"OpenAI API Error: {e}")
        time.sleep(5)
        return simple_semantic(review_text)
