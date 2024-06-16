import os
from flask import current_app, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum

db = SQLAlchemy()

class RoleEnum(Enum):
    STUDENT = "student"
    EMPLOYER = "employer"
    ADMIN = "admin"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.Enum(RoleEnum), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    about = db.Column(db.Text, nullable=True)
    avatar = db.Column(db.String(200), nullable=True)
    employer = db.relationship('Employer', backref='user', uselist=False)
    student = db.relationship('Student', backref='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def nickname(self):
        if self.role == RoleEnum.STUDENT:
            return self.student.username
        elif self.role == RoleEnum.EMPLOYER:
            return self.employer.company_name
        return self.email

    def avatar_url(self):
        if self.role == RoleEnum.STUDENT:
            if self.student.avatar_path:
                return url_for('static', filename=f'uploads/users/students/{self.student.username}/avatars/avatar.jpg')
        elif self.role == RoleEnum.EMPLOYER:
            if self.employer.avatar_path:
                return url_for('static', filename=f'uploads/users/employers/{self.employer.company_name}/avatars/avatar.jpg')
        return url_for('static', filename='icons/default_avatar.jpg')

class University(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    students = db.relationship('Student', backref='university', lazy=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100), nullable=True)
    birthdate = db.Column(db.Date, nullable=True)
    university_id = db.Column(db.Integer, db.ForeignKey('university.id'), nullable=True)
    projects = db.relationship('Project', backref='student', lazy=True, cascade="all, delete-orphan")
    avatar_path = db.Column(db.String(200), nullable=True)
    applications = db.relationship('Application', backref='student', lazy=True, cascade="all, delete-orphan")

class Employer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), unique=True, nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    avatar_path = db.Column(db.String(200), nullable=True)  # Добавить это поле
    vacancies = db.relationship('Vacancy', backref='employer', lazy=True, cascade="all, delete-orphan")

class ProjectFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(255), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'), nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(255), nullable=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'), nullable=False)
    category = db.Column(db.String(100), nullable=True)
    repository_url = db.Column(db.String(255), nullable=True)
    files = db.relationship('ProjectFile', backref='project', lazy=True, cascade="all, delete-orphan")

class Vacancy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    employer_id = db.Column(db.Integer, db.ForeignKey('employer.id', ondelete='CASCADE'), nullable=False)
    applications = db.relationship('Application', backref='vacancy', lazy=True, cascade="all, delete-orphan")
    employment_type = db.Column(db.String(50), nullable=False)
    responsibilities = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    conditions = db.Column(db.Text, nullable=False)
    key_skills = db.Column(db.Text, nullable=True)
    specialty = db.Column(db.String(100), nullable=False)

    def get_application_count(self):
        return len(self.applications)

    def get_applicants(self):
        return [application.student for application in self.applications]

    def is_applied_by_student(self, student_id):
        return Application.query.filter_by(student_id=student_id, vacancy_id=self.id).first() is not None

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'), nullable=False)
    vacancy_id = db.Column(db.Integer, db.ForeignKey('vacancy.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())