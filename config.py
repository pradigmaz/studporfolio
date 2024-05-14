import os


class Config:
    # Секретный ключ для подписи сессий и токенов CSRF
    SECRET_KEY = os.environ.get(
        "SECRET_KEY", "e66228aa0ff14623dcc2d6a77405499d3c1bf3036aa6f5f4").encode()

    SQLALCHEMY_TRACK_MODIFICATIONS = False
