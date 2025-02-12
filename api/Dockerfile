# # Используем официальный образ Python
# FROM python:3.11-slim

# # Устанавливаем рабочую директорию
# WORKDIR /app

# # Устанавливаем переменные окружения
# ENV PYTHONPATH="${PYTHONPATH}:/app"

# # Устанавливаем зависимости для работы с Firefox и geckodriver
# RUN apt-get update && apt-get install -y \
#     wget \
#     curl \
#     firefox-esr \
#     && apt-get clean

# # Скачиваем geckodriver
# RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.32.0/geckodriver-v0.32.0-linux64.tar.gz -O /tmp/geckodriver.tar.gz \
#     && tar -xvzf /tmp/geckodriver.tar.gz -C /usr/local/bin/ \
#     && rm /tmp/geckodriver.tar.gz

# # Копируем файл зависимостей
# COPY requirements.txt .

# # Устанавливаем зависимости Python
# RUN pip install --no-cache-dir -r requirements.txt

# # Копируем исходный код
# COPY . .

# # Открываем порт для Flask
# EXPOSE 5000

# # Запускаем Flask с Gunicorn
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "api.app:app"]

# Используем официальный образ Python
FROM python:3.11-slim

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

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код Flask-приложения
COPY . .

# Открываем порт для Flask
EXPOSE 5000

# Запускаем Flask с Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "api.app:app"]
