FROM python:3.11-slim
WORKDIR /app

# Копируем локальный requirements из этой же папки
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё содержимое папки security-service прямо в /app
COPY . .

EXPOSE 8080
CMD ["python", "main.py"]
