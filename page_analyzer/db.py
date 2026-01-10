import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os
from datetime import datetime
from urllib.parse import urlparse


load_dotenv()


DATABASE_URL = os.getenv('DATABASE_URL')


if not DATABASE_URL:
    DATABASE_URL = os.getenv('DB_URL')


if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres:password@localhost:5433/hexlet_project_83"

print(f"DEBUG: Используем DATABASE_URL: {DATABASE_URL}")


def db_connection():
    print(f"Подключаемся к БД: {DATABASE_URL}")
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def normalize_url(url):
    parsed = urlparse(url)
    
    normalized = parsed.netloc + parsed.path
    
    if normalized.startswith('www.'):
        normalized = normalized[4:]
    
    if normalized.endswith('/'):
        normalized = normalized[:-1]
    
    return normalized


def add_row(url):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id', (url, datetime.now()))
    new_id = cur.fetchone()[0]
    conn.commit()
    conn.close()
    return new_id


def get_url_values(id):
    conn = db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT id, name, created_at FROM urls WHERE id = %s', (id,))
    result = cur.fetchone()
    conn.close()
    return result


def is_url_exists(url):
    conn = db_connection()
    cur = conn.cursor()
    try:
        normalized_input = normalize_url(url)
        
        cur.execute('SELECT name FROM urls;')
        all_urls = cur.fetchall()
        
        for db_url in all_urls:
            normalized_db = normalize_url(db_url[0])
            if normalized_db == normalized_input:
                return True
        
        return False
    finally:
        conn.close()
        cur.close()


def get_url_id(url):
    conn = db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute('SELECT id FROM urls WHERE name = %s', (url,))
        id = cur.fetchone()
        return id
    finally:
        conn.close()


def get_all_urls():
    conn = db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute('SELECT * FROM urls;')
        all_urls = cur.fetchall()
        return all_urls
    finally:
        conn.close()


def make_url_check(url, parser_result):
    conn = db_connection()
    cur = conn.cursor()

    try:
        # Проверяем, что parser_result не None
        if parser_result is None:
            print(f"Внимание: parser_result is None для URL {url}")
            parser_result = {
                'status_code': None,
                'h1': '',
                'title': '',
                'description': ''
            }

        cur.execute('SELECT id FROM urls WHERE name=%s;', (url,))
        url_row = cur.fetchone()
        if url_row is None:
            raise ValueError(f"URL '{url}' не найден в таблице urls.")
        url_id = url_row[0]

        # Безопасное извлечение значений
        status_code = parser_result.get('status_code')
        h1 = parser_result.get('h1', '') or ''
        title = parser_result.get('title', '') or ''
        description = parser_result.get('description', '') or ''

        cur.execute('''
            INSERT INTO url_checks (
                url_id,
                status_code,
                h1,
                title,
                description,
                created_at
            ) VALUES (%s, %s, %s, %s, %s, %s);
        ''', (
            url_id,
            status_code,
            h1,
            title,
            description,
            datetime.now()
        ))

        conn.commit()
        print(f"✅ Проверка сохранена для URL: {url}")
        
    except Exception as e:
        print(f"❌ Ошибка при сохранении проверки: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def get_url_checks(url):
    conn = db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cur.execute('''SELECT * 
                    FROM url_checks 
                    JOIN urls ON url_checks.url_id = urls.id 
                    WHERE urls.name = %s;''', (url,))
        
        result = cur.fetchall()
        return result
    finally:
        conn.close()