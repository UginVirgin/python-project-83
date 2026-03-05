import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os
import logging
from datetime import datetime
from urllib.parse import urlparse, urlunparse

logger = logging.getLogger(__name__)

load_dotenv()

is_docker = os.path.exists('/.dockerenv')

if is_docker:
    # В Docker (для тестов Hexlet)
    DATABASE_URL = os.getenv('DATABASE_URL_FOR_TESTS')
else:
    # Локальная разработка
    DATABASE_URL = os.getenv('DATABASE_URL')

logger.info(f"Используем DATABASE_URL: {DATABASE_URL}")


def normalize_url(input_url):
    url_parts = urlparse(input_url)
    normalized_url = urlunparse(
        (url_parts.scheme, url_parts.netloc, '', '', '', '')
        )
    return normalized_url


def db_connection():
    logger.debug(f"Подключаемся к БД: {DATABASE_URL}")
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def add_row(url):
    conn = db_connection()
    cur = conn.cursor()
    normalized_url = normalize_url(url)
    cur.execute('''
                INSERT INTO urls (name, created_at) 
                VALUES (%s, %s) RETURNING id''', 
                (normalized_url, datetime.now()))
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


def get_url_id(url):
    conn = db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        normalized_url = normalize_url(url)
        cur.execute('SELECT id FROM urls WHERE name = %s', (normalized_url,))
        result = cur.fetchone()
        return result
    finally:
        conn.close()


def get_all_urls():
    conn = db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute('''
            SELECT urls.id, urls.name, urls.created_at, 
                   MAX(url_checks.created_at) as last_check,
                   MAX(url_checks.status_code) as status_code
            FROM urls 
            LEFT JOIN url_checks ON urls.id = url_checks.url_id
            GROUP BY urls.id
            ORDER BY urls.id DESC;
        ''')
        all_urls = cur.fetchall()
        return all_urls
    finally:
        conn.close()


def make_url_check(url_id, parser_result):
    conn = db_connection()
    cur = conn.cursor()

    try:
        if parser_result is None:
            logger.warning(f"parser_result is None для URL ID {url_id}")
            parser_result = {
                'status_code': None,
                'h1': '',
                'title': '',
                'description': ''
            }

        status_code = parser_result.get('status_code')
        h1 = parser_result.get('h1', '') or ''
        title = parser_result.get('title', '') or ''
        description = parser_result.get('description', '') or ''

        h1 = str(h1)[:255] if h1 else ''
        title = str(title)[:255] if title else ''
        description = str(description)[:255] if description else ''

        logger.debug(f"Сохраняем проверку для URL ID {url_id}:")
        logger.debug(f"  status_code: {status_code}")
        logger.debug(f"  h1: {h1}")
        logger.debug(f"  title: {title}")
        logger.debug(f"  description: {description}")

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
            datetime.now().date()
        ))

        conn.commit()
        
    except Exception as e:
        logger.error(f"❌ Ошибка при сохранении проверки: {e}", exc_info=True)
        conn.rollback()
        raise
    finally:
        conn.close()


def get_url_checks(url_id):
    """Получить все проверки для конкретного URL по его ID"""
    conn = db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cur.execute('''SELECT * 
                    FROM url_checks 
                    WHERE url_id = %s
                    ORDER BY created_at DESC;''', (url_id,))
        
        result = cur.fetchall()
        logger.debug(f"Найдено {len(result)} проверок для URL ID {url_id}")
        return result
    finally:
        conn.close()