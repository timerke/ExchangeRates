"""Модуль запускает веб-приложение."""

from app import app


if __name__ == '__main__':
    app.run(debug=True)
