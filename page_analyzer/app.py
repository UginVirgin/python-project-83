import os
from dotenv import load_dotenv
from flask import Flask

load_dotenv()
app = Flask(__name__)
app.config['SECERT_KEY'] = os.getenv('SECRET_KEY')

@app.route('/')
def hello():
    return "hello world"