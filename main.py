import os
from flask import Flask
from routes import auth_bp, project_bp, vacancy_bp, filters_bp, application_bp, main_bp, profile_bp, settings_bp, search_bp
from config import Config
from models import University, db, User, Student, Employer, RoleEnum
from flask_login import LoginManager
import logging
from werkzeug.serving import WSGIRequestHandler
from universities import UNIVERSITIES

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

@app.context_processor
def inject_role_enum():
    return dict(RoleEnum=RoleEnum)

@app.template_filter('basename')
def basename_filter(path):
    return os.path.basename(path)

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(project_bp)
app.register_blueprint(vacancy_bp)
app.register_blueprint(filters_bp)
app.register_blueprint(application_bp)
app.register_blueprint(search_bp)

class UTF8RequestHandler(WSGIRequestHandler):
    def send_response(self, code, message=None):
        self._headers_buffer = []
        self._headers_buffer.append(("%s %d %s\r\n" %
                                     (self.protocol_version, code, message)).encode('utf-8', 'strict'))
        self.send_header('Content-Type', 'text/html; charset=utf-8')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
                # Загрузка университетов в БД
        if not University.query.first():
            for uni_name in UNIVERSITIES:
                university = University(name=uni_name)
                db.session.add(university)
            db.session.commit()

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

    app.run(debug=True, use_reloader=True, request_handler=UTF8RequestHandler)