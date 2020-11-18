"""Модуль с определением функций представления."""

import json
from flask import make_response, render_template, request
import app.utils as u
from app import app, db
from .cbr import Cbr


@app.route('/about')
def about():
    """Функция представления отображает страницу с информацией."""

    return render_template('about.html')


@app.route('/')
def index():
    """Функция представления отображает главную страницу."""

    valutas = u.get_valutas()  # список валют из ЦБР
    return render_template('index.html', valutas=valutas)


@app.route('/get_exchanges', methods=['post', 'get'])
def get_exchanges():
    """Функция представления обрабатывает запрос на получение курсов валют."""

    if request.method == 'POST':
        data = json.loads(request.get_data().decode('utf-8'))
        codes = data['data']  # список кодов требуемых валют
        period = data['period']  # начало и конец периода
        if not u.check_data(codes, period):
            # Переданы неверные данные
            return make_response(({'text': 'Неверные данные'}, 400))
        exchanges = u.get_exchanges(codes, period)
        # По какому параметру нужно отсортировать данные
        sort_by = data.get('sort_by')
        if sorted:
            # Данные нужно отсортировать
            if sort_by == 'Валюта':
                index1, index2 = 0, 2
            elif sort_by == 'Курс':
                index1, index2 = 1, 0
            else:
                index1, index2 = 2, 0
            exchanges = sorted(exchanges, key=lambda x: (x[index1], x[index2]))
        return make_response(({'exchanges': exchanges}, 200))
    return make_response(({}, 400))
