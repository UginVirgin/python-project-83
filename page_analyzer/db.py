import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os
from datetime import datetime


load_dotenv()

# ПРОБЛЕМА: вы используете DB_URL, но должно быть DATABASE_URL
# В вашем .env файле у вас DATABASE_URL
DATABASE_URL = os.getenv('DATABASE_URL')

# Если DATABASE_URL не установлен, используем значение по умолчанию для Docker
if not DATABASE_URL:
    DATABASE_URL = os.getenv('DB_URL')  # Старое имя переменной
    print(f"DEBUG: Используем DB_URL: {DATABASE_URL}")

if not DATABASE_URL:
    # Значение по умолчанию для Docker Compose
    DATABASE_URL = "postgresql://postgres:password@db:5432/page_analyzer"
    print(f"DEBUG: Используем значение по умолчанию: {DATABASE_URL}")

print(f"DEBUG: Итоговый DATABASE_URL: {DATABASE_URL}")


def db_connection():
    print(f"DEBUG db_connection(): Подключаемся к: '{DATABASE_URL}'")
    
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL не установлен!")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("DEBUG: Подключение успешно установлено!")
        return conn
    except psycopg2.OperationalError as e:
        print(f"❌ Ошибка подключения: {e}")
        print(f"🔧 Пробуем исправить URL...")
        
        # Пробуем разные варианты
        test_urls = [
            DATABASE_URL,
            DATABASE_URL.replace("localhost", "db"),
            DATABASE_URL.replace("5433", "5432"),
            "postgresql://postgres:password@db:5432/page_analyzer",
        ]
        
        for test_url in test_urls:
            if test_url == DATABASE_URL:
                continue
            try:
                print(f"  Пробуем: {test_url}")
                conn = psycopg2.connect(test_url)
                print(f"  ✅ Успешно! Используем: {test_url}")
                # Обновляем глобальную переменную
                global DATABASE_URL
                DATABASE_URL = test_url
                return conn
            except Exception as e2:
                print(f"  ❌ Не удалось: {e2}")
                continue
        
        raise
