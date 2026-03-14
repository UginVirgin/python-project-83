import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, request, flash, url_for
from .db import (add_row, get_url_values, is_url_exists, 
                 get_url_id, get_all_urls, make_url_check, 
                 get_url_checks)
from .url_parser import url_parser
import validators
import logging

ALERT_SUCCESS = 'alert-success'
ALERT_DANGER = 'alert-danger'

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def hello():
    logger.debug("Это hello")
    return render_template("index.html")


def normalize_url(raw: str) -> str:
    parsed = urlparse(raw)
    return f"{parsed.scheme}://{parsed.netloc}"


@app.route('/urls', methods=['POST', 'GET'])
def urls():
    if request.method == 'POST':
        raw_url = request.form.get('url', '').strip()

        if not validators.url(raw_url):
            flash('Некорректный URL', category=ALERT_DANGER)
            return render_template('index.html'), 422

        normalized_url = normalize_url(raw_url)

        if is_url_exists(normalized_url):
            flash('Страница уже существует', category=ALERT_SUCCESS)
            url_id_result = get_url_id(normalized_url)
            if url_id_result and 'id' in url_id_result:
                return redirect(url_for('urls_check', id=url_id_result['id']))

            flash('Ошибка: не найден ID URL', category=ALERT_DANGER)
            return redirect(url_for('hello'))

        new_row_id = add_row(normalized_url)
        flash('Страница успешно добавлена', category=ALERT_SUCCESS)
        return redirect(url_for('urls_check', id=new_row_id))

    urls = get_all_urls()
    return render_template('urls.html', urls=urls)


@app.route('/urls/<id>', methods=['POST', 'GET'])
def urls_check(id):
    url_values = get_url_values(id)
    if not url_values:
        flash('URL не найден', category=ALERT_DANGER)
        return redirect(url_for('urls'))

    url_checks = get_url_checks(id)
    logger.debug("Получено %s проверок для URL ID %s", len(url_checks), id)

    return render_template('url_id.html', url_values=url_values, checks=url_checks)


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_url_info(id):
    url_data = get_url_values(id)
    if not url_data:
        flash('URL не найден', ALERT_DANGER)
        return redirect(url_for('urls'))
    
    url = url_data["name"]
    
    try:
        parser_result = url_parser(url)
        logger.debug(f"Результат парсера для {url}: {parser_result}")
        
        if parser_result is None or parser_result.get('status_code') is None:
            flash('Произошла ошибка при проверке', ALERT_DANGER)
        else:
            # Исправлено: передаем ID, а не имя URL
            make_url_check(id, parser_result)
            flash('Страница успешно проверена', ALERT_SUCCESS)
            
    except Exception as e:
        logger.error(f"Исключение при проверке URL ID {id}: {e}", exc_info=True)
        flash('Произошла ошибка при проверке', ALERT_DANGER)
    
    return redirect(url_for('urls_check', id=id))