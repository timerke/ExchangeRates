"""Модуль с определениями таблиц базы данных."""

from app import db


class Valuta(db.Model):
    """Таблица с именами и кодами валют."""

    __tablename__ = 'valutas'
    # Id валюты
    id = db.Column(db.Integer(), primary_key=True)
    # Имя валюты
    name = db.Column(db.String, nullable=False)
    # Код валюты
    code = db.Column(db.String, nullable=False)
    # Добавляем связь с таблице
    exchange = db.relationship('Exchange', backref='valuta')

    def __init__(self, name, code):
        """Конструктор таблицы."""

        self.name = name
        self.code = code

    def __repr__(self):
        return f'<Valuta({self.id}, {self.name}, {self.code})>'


class Exchange(db.Model):
    """Таблица с курсами валют."""

    __tablename__ = 'exchanges'
    # Id записи
    id = db.Column(db.Integer(), primary_key=True)
    # Дата курса
    date = db.Column(db.Date(), nullable=False)
    # Курс
    exchange = db.Column(db.Float(), nullable=False)
    # Id валюты, для которой указан курс
    valuta_id = db.Column(db.Integer(), db.ForeignKey('valutas.id'))

    def __init__(self, date, exchange, valuta):
        """Конструктор таблицы."""

        self.date = date
        self.exchange = exchange
        self.valuta_id = valuta.id

    def __repr__(self):
        return f'<Exchange({self.id}, {self.date}, {self.exchange},\
            {self.valuta_id})>'
