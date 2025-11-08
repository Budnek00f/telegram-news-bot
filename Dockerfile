FROM python:3.9-slim

WORKDIR /app

# Обновляем пакеты и устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt первым для кэширования
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Создаем директорию для логов
RUN mkdir -p logs

# Запускаем приложение
CMD ["python", "scheduler.py"]
