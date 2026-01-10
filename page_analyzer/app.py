import os
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, request, flash, url_for
from .db import add_row, get_url_values, is_url_exists, get_url_id, get_all_urls, make_url_check, get_url_checks
from .url_parser import url_parser
import validators


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def hello():
    print("Это hello")
    return render_template("index.html")


@app.route('/urls', methods=['POST', 'GET'])
def urls():
    if request.method == 'POST':
        url = request.form['url']
        if validators.url(url):
            if is_url_exists(url):
                flash('Страница уже существует', category='alert-success')
                url_id_result = get_url_id(url)
                if url_id_result and 'id' in url_id_result:
                    id = url_id_result['id']
                    result = redirect(url_for('urls_check', id=id))
                else:
                    flash('Ошибка: не найден ID URL', 'danger')
                    result = redirect(url_for('hello'))
            else:
                new_row_id = add_row(url)
                flash('Страница успешно добавлена', category='alert-success')
                result = redirect(url_for('urls_check', id=new_row_id))
        else:
            flash('Некорректный URL', category='alert-danger')
            result = render_template('index.html'), 422
        return result
    
    urls = get_all_urls()
    return render_template('urls.html', urls=urls)


@app.route('/urls/<id>', methods=['POST', 'GET'])
def urls_check(id):
    url_values = get_url_values(id)
    url_name = url_values['name']
    print(url_values)

    url_checks = get_url_checks(url_name)

    return render_template('url_id.html', url_values=url_values, checks=url_checks)


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_url_info(id):
    url = get_url_values(id)["name"]
    
    try:
        parser_result = url_parser(url)
        print(f"DEBUG: Результат парсера для {url}: {parser_result}")
        
        if parser_result is None or parser_result.get('status_code') is None:
            flash('Произошла ошибка при проверке', 'danger')
        else:
            make_url_check(url, parser_result)
            flash('Страница успешно проверена', 'success')
            
    except Exception as e:
        print(f"Ошибка в check_url_info: {e}")
        flash('Произошла ошибка при проверке', 'danger')
    
    return redirect(url_for('urls_check', id=id))

