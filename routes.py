from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Student, Employer, RoleEnum
from forms import RegistrationFormStudent, RegistrationFormEmployer, LoginForm
import logging

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    logging.debug("Rendering index page")
    student_form = RegistrationFormStudent()
    employer_form = RegistrationFormEmployer()
    login_form = LoginForm()
    return render_template('index.html', student_form=student_form, employer_form=employer_form, login_form=login_form)


@auth_bp.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationFormStudent()
    if form.validate_on_submit():
        user = User(email=form.email.data, role=RoleEnum.STUDENT)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        student = Student(user_id=user.id, first_name=form.first_name.data,
                          last_name=form.last_name.data, middle_name=form.middle_name.data)
        db.session.add(student)
        db.session.commit()
        login_user(user)
        logging.info(f"Student {user.email} registered successfully")
        flash('Регистрация прошла успешно!', 'success')
        return redirect(url_for('auth.student_profile', student_id=student.id))
    logging.warning("Student registration form validation failed")
    return render_template('index.html', student_form=form, employer_form=RegistrationFormEmployer(), login_form=LoginForm(), form=form)


@auth_bp.route('/register/employer', methods=['GET', 'POST'])
def register_employer():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationFormEmployer()
    if form.validate_on_submit():
        user = User(email=form.email.data, role=RoleEnum.EMPLOYER)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        employer = Employer(
            user_id=user.id, company_name=form.company_name.data)
        db.session.add(employer)
        db.session.commit()
        login_user(user)
        logging.info(f"Employer {user.email} registered successfully")
        flash('Регистрация прошла успешно!', 'success')
        return redirect(url_for('auth.employer_profile', employer_id=employer.id))
    logging.warning("Employer registration form validation failed")
    return render_template('index.html', student_form=RegistrationFormStudent(), employer_form=form, login_form=LoginForm(), form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            logging.info(f"User {user.email} logged in successfully")
            flash('Вход выполнен успешно!', 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            elif user.role == RoleEnum.STUDENT:
                student = Student.query.filter_by(user_id=user.id).first()
                return redirect(url_for('auth.student_profile', username=student.username))
            elif user.role == RoleEnum.EMPLOYER:
                employer = Employer.query.filter_by(user_id=user.id).first()
                return redirect(url_for('auth.employer_profile', company_name=employer.company_name))
            else:
                return redirect(url_for('main.index'))
        else:
            logging.warning(f"Failed login attempt for {form.email.data}")
            flash('Неправильный email или пароль', 'danger')
    return render_template('index.html', student_form=RegistrationFormStudent(), employer_form=RegistrationFormEmployer(), login_form=LoginForm())


@auth_bp.route('/logout')
@login_required
def logout():
    logging.info(f"User {current_user.email} logged out")
    logout_user()
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('auth.index'))


@auth_bp.route('/profile/student/<username>')
@login_required
def student_profile(username):
    student = Student.query.filter_by(username=username).first_or_404()
    logging.debug(f"Rendering profile for student {username}")
    return render_template('profile_students.html', student=student)


@auth_bp.route('/profile/employer/<company_name>')
@login_required
def employer_profile(company_name):
    employer = Employer.query.filter_by(
        company_name=company_name).first_or_404()
    logging.debug(f"Rendering profile for employer {company_name}")
    return render_template('profile_employers.html', employer=employer)

@auth_bp.route('/students')
def students():
    logging.debug("Rendering students page")
    return render_template('presentation_students.html', student_form=RegistrationFormStudent(), employer_form=RegistrationFormEmployer(), login_form=LoginForm())


@auth_bp.route('/employers')
def employers():
    logging.debug("Rendering employers page")
    return render_template('presentation_employers.html', employer_form=RegistrationFormEmployer(), login_form=LoginForm(), student_form=RegistrationFormStudent())
