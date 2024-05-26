from flask import Flask
from config import Config
from models import db, User, Student, Employer, RoleEnum
from routes import auth_bp
from flask_login import LoginManager
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s')

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app.register_blueprint(auth_bp)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        if not Student.query.filter_by(username='teststudent').first():
            student_user = User(email='teststudent@example.com',
                                password_hash='', role=RoleEnum.STUDENT)
            student_user.set_password('password')
            db.session.add(student_user)
            db.session.commit()
            student = Student(user_id=student_user.id, username='teststudent',
                              first_name='Иван', last_name='Иванов')
            db.session.add(student)

        if not Employer.query.filter_by(company_name='Test Company').first():
            employer_user = User(
                email='testemployer@example.com', password_hash='', role=RoleEnum.EMPLOYER)
            employer_user.set_password('password')
            db.session.add(employer_user)
            db.session.commit()
            employer = Employer(user_id=employer_user.id,
                                company_name='Test Company')
            db.session.add(employer)

        db.session.commit()

    app.run(debug=True, use_reloader=True)
