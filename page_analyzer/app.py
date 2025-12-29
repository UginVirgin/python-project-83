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
    print('это urls')
    if request.method == 'POST':
        print('post')
        url = request.form['url']
        if validators.url(url):
            if is_url_exists(url):
                flash('Страница уже существует', category='alert alert-success')
                id = get_url_id(url)['id']
                result = redirect(url_for('urls_check', id=id))
            else:
                new_row_id = add_row(url)
                print('это urls validators')
                flash('Страница успешно добавлена', category='alert alert-success')
                result = redirect(url_for('urls_check', id=new_row_id))
        else:
            flash('Некорректный URL', category='alert alert-danger')
            result = render_template('index.html'), 422
        print(url)
        return result
    
    urls = get_all_urls()
    return render_template('urls.html',urls=urls)


@app.route('/urls/<id>', methods=['POST', 'GET'])
def urls_check(id):
    print('это urls_check')
    url_values = get_url_values(id)
    url_name = url_values['name']
    print(url_values)

    url_checks = get_url_checks(url_name)

    return render_template('url_id.html', url_values=url_values, checks=url_checks)


@app.route('/urls/<int:id>/checks', methods=['POST', 'GET'])
def check_url_info(id):
    url = get_url_values(id)["name"]
    print('это check_url_info')
    parser_result = url_parser(url)
    print(parser_result)
    make_url_check(url, parser_result)

    return redirect(url_for('urls_check', id=id))

