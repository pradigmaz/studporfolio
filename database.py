from flask_sqlalchemy import SQLAlchemy
from create_db import create_admin_student_account, create_admin_employer_account

db = SQLAlchemy()

def init_db(app):
    with app.app_context():
        db.create_all()
        create_admin_student_account()
        create_admin_employer_account()
