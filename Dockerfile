# Используем официальный образ Python
FROM python:3.11-slim as base

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем переменные окружения
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Устанавливаем зависимости для работы с Firefox и geckodriver
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    firefox-esr \
    && apt-get clean

# Скачиваем geckodriver
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.32.0/geckodriver-v0.32.0-linux64.tar.gz -O /tmp/geckodriver.tar.gz \
    && tar -xvzf /tmp/geckodriver.tar.gz -C /usr/local/bin/ \
    && rm /tmp/geckodriver.tar.gz

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Стадия для Flask
FROM base as flask
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "api.app:app"]

# Стадия для бота
FROM base as bot
CMD ["python", "bot/bot_main.py"]
