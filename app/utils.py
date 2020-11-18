"""Модуль содержит функции, используемые в веб-приложении."""

import datetime
from app import db
from .cbr import Cbr
from .models import Exchange, Valuta


def check_data(valutas, period):
    """Функция проверяет, что данные для запроса верные.
    :param valutas: список кодов валют;
    :param period: начало и конец периода поиска курсов валют.
    :return: True, если данные переданы верно."""

    if valutas and (period[0] or period[1]):
        return True
    return False


def get_codes(codes):
    """Функция проверяет, есть ли в списке кодов валют ключевое слово all.
    Если ключевое слово есть, нужно получить курсы всех валют."""

    if 'all' in codes:
        return ['all']
    return codes


def get_dates(period):
    """Функция создает объекты datetime для начала и конца периода.
    :param period: список из начала и конца периода."""

    start_date, finish_date = period
    # Если начало или конец периода не указан, то начало и конец совпадают
    if not start_date and finish_date:
        start_date = finish_date
    elif start_date and not finish_date:
        finish_date = start_date
    # Начальная дата должна быть не больше конечной
    if start_date > finish_date:
        swap = finish_date
        finish_date = start_date
        start_date = swap
    # Проверяем, что сегодняшняя дата не больше начала и конца периода
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    if today < start_date:
        start_date = today
    if today < finish_date:
        finish_date = today
    # Извлекаем год, месяц и день
    start_date = map(int, start_date.split('-'))
    finish_date = map(int, finish_date.split('-'))
    # Создаем объекты datetime
    return datetime.date(*start_date), datetime.date(*finish_date)


def get_exchanges(codes, period):
    """Функция получает курсы валют за заданный период.
    :param codes: список кодов валют, для которых нужно получить курсы валют;
    :param period: даты начала и конца периода, для которого нужно получить
    курсы валют.
    :return: список курсов валют в виде словарей: {code: код валюты,
    name: имя валюты, exchange: курс, date: дата}."""

    # Получаем начало и конец периода
    start_date, finish_date = get_dates(period)
    print(start_date, finish_date)
    # Определяем коды валют
    codes = get_codes(codes)
    # Заполняем базу данных курсами валют за требуемые даты
    date = start_date
    while date <= finish_date:
        if db.session.query(Exchange.date).filter(Exchange.date == date).count() == 0:
            # В базе данных нет курсов валют в день date. Запрашиваем данные
            # из ЦБР
            cbr = Cbr()
            exchanges = cbr.get_exchanges(date.strftime('%Y-%m-%d'))
            # Добавляем данные в таблицу
            exchanges_for_db = []
            for e in exchanges:
                # Находим в базе данных валюту
                valuta = db.session.query(Valuta).filter(Valuta.name == e['name'],
                                                         Valuta.code == e['code']).first()
                # Создаем объект модели Exchange и добавляем в список
                exchange_for_db = Exchange(
                    date=date, exchange=e['exchange'], valuta=valuta)
                exchanges_for_db.append(exchange_for_db)
            db.session.add_all(exchanges_for_db)
            db.session.commit()
            print(f'[{date.strftime("%Y-%m-%d")}][Курсы валют записаны]')
        date += datetime.timedelta(days=1)
    # Из базы данных получаем данные о курсе требуемых валют за требуемые даты
    result = []
    for code in codes:
        query = db.session.query(Valuta.name, Exchange.exchange,
                                 Exchange.date)
        query = query.join(Exchange, Valuta.id == Exchange.valuta_id)
        if code == 'all':
            result = query.filter(start_date <= Exchange.date,
                                  Exchange.date <= finish_date).all()
            break
        e = query.filter(Valuta.code == code, start_date <= Exchange.date,
                         Exchange.date <= finish_date).order_by(Exchange.date).all()
        result = [*result, *e]
    return result


def get_valutas():
    """Функция проверяет, заполнена ли таблицы valutas из базы данных. Если
    таблица пустая, она заполняется.
    :return: список словарей валют из базы данных. Формат словаря:
    {code: код валюты, name: имя валюты}."""

    if db.session.query(Valuta).count() == 0:
        # Таблица пустая. Запрашиваем валюты из ЦБР
        cbr = Cbr()
        valutas = cbr.get_valutas()
        # Добавляем данные в таблицу
        valutas_for_db = [Valuta(name=v['name'], code=v['code'])
                          for v in valutas]
        db.session.add_all(valutas_for_db)
        db.session.commit()
    # В таблице есть данные, получаем их
    valutas_from_db = db.session.query(Valuta).order_by(Valuta.name).all()
    # Создаем список
    valutas = []
    for valuta in valutas_from_db:
        data = {'code': valuta.code, 'name': valuta.name}
        valutas.append(data)
    return valutas
