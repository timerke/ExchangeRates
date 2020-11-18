"""Модуль с объявлением экземпляра веб-приложения."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

# Путь к директории с веб-приложением
BASE_DIR = Path(__file__).resolve().parent.parent

# Cоздаем экземпляр приложения
app = Flask(__name__, static_folder='../static',
            template_folder='../templates')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{BASE_DIR}/db.sqlite'

# База данных
db = SQLAlchemy(app)
from . import models
db.create_all()

# Указываем на функции представления
from . import views
