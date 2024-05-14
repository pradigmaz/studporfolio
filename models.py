from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import SubmitField
from database import db
from sqlalchemy import or_


class User(UserMixin, db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone_number = db.Column(db.String(20), unique=True,nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    avatar_url = db.Column(db.String(500))
    about = db.Column(db.String(1000))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Students(User, UserMixin):
    surname = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True,nullable=False, index=True)
    role = db.Column(db.String(20), default='student')
    portfolio_files = db.relationship('PortfolioFile', backref='student', lazy=True)
    projects = db.relationship('Project', backref='student', lazy=True)

    @classmethod
    def register(cls, surname, first_name, middle_name, username, phone_number, email, password):
        existing_user = cls.query.filter(
            or_(
                cls.username == username,
                cls.phone_number == phone_number,
                cls.email == email
            )
        ).first()
        if existing_user:
            error_msg = "An account with this {} already exists."
            if existing_user.username == username:
                raise ValueError(error_msg.format("username"))
            if existing_user.phone_number == phone_number:
                raise ValueError(error_msg.format("phone number"))
            if existing_user.email == email:
                raise ValueError(error_msg.format("email"))

        student = cls(surname=surname, first_name=first_name, middle_name=middle_name,username=username, phone_number=phone_number, email=email)
        student.set_password(password)
        db.session.add(student)
        db.session.commit()
        return student

    @classmethod
    def authenticate(cls, username, password):
        student = cls.query.filter_by(username=username).first()
        if student and student.check_password(password):
            return student
        return None


class Employers(User, UserMixin):
    company_name = db.Column(db.String(100), nullable=False)
    contact_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='employer')

    @classmethod
    def register(cls, company_name, contact_name, email, phone_number, password):
        existing_employer = cls.query.filter(
            (cls.email == email) | (cls.phone_number == phone_number)).first()
        if existing_employer:
            error_msg = {}
            if existing_employer.email == email:
                error_msg['email'] = 'Email already exists'
            if existing_employer.phone_number == phone_number:
                error_msg['phone_number'] = 'Phone number already exists'
            if error_msg:
                return error_msg  # Return dictionary of errors

        employer = cls(
            company_name=company_name,
            contact_name=contact_name,
            email=email,
            phone_number=phone_number
        )
        employer.set_password(password)
        db.session.add(employer)
        db.session.commit()
        return employer

    @classmethod
    def authenticate(cls, email, password):
        employer = cls.query.filter_by(email=email).first()
        if employer and employer.check_password(password):
            return employer
        return None


class PortfolioFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PortfolioFile {self.file_name} uploaded on {self.upload_date}>'


FIELD_CHOICES = [
    ('tech', 'Технологии'),
    ('health', 'Здравоохранение'),
    ('edu', 'Образование'),
    ('sport', 'Спорт'),
    ('art', 'Искусство'),
    ('science', 'Наука'),
    ('business', 'Бизнес'),
    ('psychology', 'Психология')
]

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False,index=True)  # Добавлен индекс
    description = db.Column(db.Text)
    field = db.Column(db.String(100), db.Enum(*[choice[0] for choice in FIELD_CHOICES], name="field_types"), nullable=False, index=True)  # Добавлен индекс
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)  # Добавлен индекс
    files = db.relationship('ProjectFile', backref='project',lazy='dynamic', cascade='all, delete-orphan')
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Project {self.title}>'

    def add_file(self, file):
        self.files.append(file)
        db.session.commit()

    def remove_file(self, file):
        self.files.remove(file)
        db.session.commit()


class ProjectFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)


class Vacancy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    employment_type = db.Column(db.String(100), nullable=False)
    responsibilities = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    conditions = db.Column(db.Text, nullable=False)
    key_skills = db.Column(db.Text, nullable=False)
    employer_id = db.Column(db.Integer, db.ForeignKey('employers.id'), nullable=False, index=True)  # Добавлен индекс
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    field = db.Column(db.String(25), index=True)  # Добавлен индекс

    employer = db.relationship('Employers', backref=db.backref('vacancies', lazy='dynamic'))  # Изменено на dynamic

    def set_active(self, active):
        self.is_active = active
        db.session.commit()

    def update(self, **kwargs):
        protected_keys = ['id', 'created_at']  # Защита ключевых полей
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None and key not in protected_keys:
                setattr(self, key, value)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def create(cls, **kwargs):
        new_vacancy = cls(**kwargs)
        db.session.add(new_vacancy)
        db.session.commit()
        return new_vacancy
