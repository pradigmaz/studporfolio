import os


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY", "e66228aa0ff14623dcc2d6a77405499d3c1bf3036aa6f5f4").encode()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///site.db")
    DEBUG = os.environ.get("FLASK_DEBUG", False)
    TESTING = os.environ.get("FLASK_TESTING", False)
