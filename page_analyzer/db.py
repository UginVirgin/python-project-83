import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os
from datetime import datetime


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def db_connection():
    print(f"Данные для подключения: '{DATABASE_URL}'")
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def add_row(url):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id', (url, datetime.now()))
    new_id = cur.fetchone()[0]
    conn.commit()
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
        cur.execute('SELECT id FROM urls WHERE name = %s;', (url,))
        result = cur.fetchone()
        if result:
            return True
        else:
            return False
    finally:
        conn.close()
        cur.close()


def get_url_id(url):
    conn = db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT id FROM urls WHERE name = %s', (url,))
    id = cur.fetchone()
    return id


def get_all_urls():
    conn = db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM urls;')
    all_urls = cur.fetchall()
    return all_urls


def make_url_check(url, parser_result):
    conn = db_connection()
    cur = conn.cursor()

    cur.execute('SELECT id FROM urls WHERE name=%s;', (url,))
    url_row = cur.fetchone()
    if url_row is None:
        conn.close()
        raise ValueError(f"URL '{url}' не найден в таблице urls.")
    url_id = url_row[0]

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
        parser_result['status_code'],
        parser_result['h1'],
        parser_result['title'],
        parser_result['description'],
        datetime.now()
    ))

    conn.commit()
    conn.close()


def get_url_checks(url):
    conn = db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute('''SELECT * 
                FROM url_checks 
                JOIN urls ON url_checks.url_id = urls.id 
                WHERE urls.name = %s;''', (url,))
    
    result = cur.fetchall()
    return result
    
    
    
