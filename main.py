from flask import Flask, url_for
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
from models import *
from data import *
from database import db, init_db
from flask_migrate import Migrate
import os

app = Flask(__name__)
app.config.from_object(Config)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
migrate = Migrate(app, db)


# Пути к папкам
# Корневая папка для пользовательских данных
app.config['USER_FOLDERS_ROOT'] = os.path.join('data', 'users', )

# Разрешенные расширения для аватаров
ALLOWED_AVATAR_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['ALLOWED_AVATAR_EXTENSIONS'] = ALLOWED_AVATAR_EXTENSIONS

# Разрешенные расширения для обычных файлов (исключаем изображения)
ALLOWED_FILE_EXTENSIONS = {'pdf', 'docx', 'pptx'}
app.config['ALLOWED_FILE_EXTENSIONS'] = ALLOWED_FILE_EXTENSIONS


def get_user_folder(username, role):
    # Определяем путь к папке в зависимости от роли пользователя
    if role == 'student':
        base_folder = os.path.join(app.config['USER_FOLDERS_ROOT'], 'students')
    elif role == 'employer':
        base_folder = os.path.join(app.config['USER_FOLDERS_ROOT'], 'employers')
    else:
        raise ValueError("Неизвестная роль пользователя")

    # Создаем папку пользователя в соответствующей директории
    user_folder = os.path.join(base_folder, username)
    os.makedirs(user_folder, exist_ok=True)
    return user_folder


def get_user_avatar_folder(username, role):
    avatar_folder = os.path.join(get_user_folder(username, role), 'avatars')
    os.makedirs(avatar_folder, exist_ok=True)
    return avatar_folder


def get_user_upload_folder(username, role):
    upload_folder = os.path.join(get_user_folder(username, role), 'upload')
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder



bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Фильтр шаблона 'basename' для извлечения базового имени файла из полного пути
@app.template_filter('basename')
def basename_filter(s):
    return os.path.basename(s)


@app.template_filter('avatar_url')
def avatar_url_filter(avatar_path, username):
    if avatar_path:
        filename = os.path.basename(avatar_path)
        return url_for('user_avatar_students', username=username, filename=filename) 
    else:
        return url_for('static', filename='icons/i.jpg')


with app.app_context():
    init_db(app)

from routes import *


if __name__ == "__main__":
    
    app.run(debug=True, host='0.0.0.0')
