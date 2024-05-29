from flask import Blueprint, render_template, redirect, url_for, request, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import Application, db, User, Student, Employer, RoleEnum, Project, Vacancy
from forms import ApplicationForm, RegistrationFormStudent, RegistrationFormEmployer, LoginForm, UpdateAvatarForm, UpdateEmailForm, UpdatePasswordForm, ProjectForm, VacancyForm
from werkzeug.utils import secure_filename
import os
import logging

auth_bp = Blueprint('auth', __name__)
project_bp = Blueprint('project', __name__)
vacancy_bp = Blueprint('vacancy', __name__)
filters_bp = Blueprint('filters', __name__)
application_bp = Blueprint('application', __name__)

@filters_bp.app_template_filter()
def avatar_url(avatar_url, username):
    if avatar_url:
        return avatar_url
    return f'/static/icons/default_avatar.png'


@auth_bp.route('/')
def index():
    logging.debug("Rendering index page")
    student_form = RegistrationFormStudent()
    employer_form = RegistrationFormEmployer()
    login_form = LoginForm()
    return render_template('index.html', student_form=student_form, employer_form=employer_form, login_form=login_form, RoleEnum=RoleEnum)


@auth_bp.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
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
        return redirect(url_for('auth.student_profile', student_id=student.id))
    logging.warning("Student registration form validation failed")
    return render_template('index.html', student_form=form, employer_form=RegistrationFormEmployer(), login_form=LoginForm(), form=form)


@auth_bp.route('/register/employer', methods=['GET', 'POST'])
def register_employer():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
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
        return redirect(url_for('auth.employer_profile', employer_id=employer.id))
    logging.warning("Employer registration form validation failed")
    return render_template('index.html', student_form=RegistrationFormStudent(), employer_form=form, login_form=LoginForm(), form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            logging.info(f"Пользователь {user.email} успешно вошел")
            next_page = request.args.get('next')
            if next_page:
                redirect_url = next_page
            elif user.role == RoleEnum.STUDENT:
                student = Student.query.filter_by(user_id=user.id).first()
                redirect_url = url_for('auth.student_profile', username=student.username)
            elif user.role == RoleEnum.EMPLOYER:
                employer = Employer.query.filter_by(user_id=user.id).first()
                redirect_url = url_for('auth.employer_profile', company_name=employer.company_name)
            else:
                redirect_url = url_for('auth.index')

            return jsonify({'redirect': redirect_url}) if request.is_json else redirect(redirect_url)
        else:
            logging.warning(f"Неудачная попытка входа для {form.email.data}")
            return jsonify({'error': 'Неверный email или пароль'}), 400 if request.is_json else render_template('index.html', student_form=RegistrationFormStudent(), employer_form=RegistrationFormEmployer(), login_form=LoginForm())
    return jsonify({'error': 'Ошибка валидации формы'}), 400 if request.is_json else render_template('index.html', student_form=RegistrationFormStudent(), employer_form=RegistrationFormEmployer(), login_form=LoginForm())


@auth_bp.route('/logout')
@login_required
def logout():
    logging.info(f"User {current_user.email} logged out")
    logout_user()
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


@auth_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    avatar_form = UpdateAvatarForm()
    email_form = UpdateEmailForm()
    password_form = UpdatePasswordForm()

    if current_user.role == RoleEnum.STUDENT:
        student = Student.query.filter_by(user_id=current_user.id).first()
    elif current_user.role == RoleEnum.EMPLOYER:
        employer = Employer.query.filter_by(user_id=current_user.id).first()

    if avatar_form.validate_on_submit():
        if avatar_form.avatar.data:
            current_user.save_avatar(avatar_form.avatar.data)
            db.session.commit()
    elif email_form.validate_on_submit():
        current_user.email = email_form.email.data
        db.session.commit()
    elif password_form.validate_on_submit():
        if current_user.check_password(password_form.current_password.data):
            current_user.set_password(password_form.new_password.data)
            db.session.commit()

    if current_user.role == RoleEnum.STUDENT:
        return render_template('settings_students.html', student=student, avatar_form=avatar_form, email_form=email_form, password_form=password_form)
    elif current_user.role == RoleEnum.EMPLOYER:
        return render_template('settings_employers.html', employer=employer, avatar_form=avatar_form, email_form=email_form, password_form=password_form)
    else:
        return redirect(url_for('auth.index'))


@project_bp.route('/projects')
@login_required
def list_projects():
    projects = Project.query.filter_by(
        student_id=current_user.student.id).all()
    return render_template('project_list.html', projects=projects)


@project_bp.route('/projects/create', methods=['GET', 'POST'])
@login_required
def create_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            title=form.title.data,
            description=form.description.data,
            student_id=current_user.student.id
        )
        if form.file.data:
            filename = secure_filename(form.file.data.filename)
            file_path = os.path.join(
                current_app.root_path, 'uploads', filename)
            form.file.data.save(file_path)
            project.file_path = file_path
        db.session.add(project)
        db.session.commit()
        return redirect(url_for('project.list_projects'))
    return render_template('project_creation.html', form=form)


@project_bp.route('/projects/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        project.title = form.title.data
        project.description = form.description.data
        if form.file.data:
            filename = secure_filename(form.file.data.filename)
            file_path = os.path.join(
                current_app.root_path, 'uploads', filename)
            form.file.data.save(file_path)
            project.file_path = file_path
        db.session.commit()
        return redirect(url_for('project.list_projects'))
    return render_template('project_editing.html', form=form)


@vacancy_bp.route('/vacancies')
@login_required
def list_vacancies():
    vacancies = Vacancy.query.filter_by(
        employer_id=current_user.employer.id).all()
    return render_template('vacancy_list.html', vacancies=vacancies)


@vacancy_bp.route('/vacancies/delete/<int:vacancy_id>', methods=['POST'])
@login_required
def delete_vacancy(vacancy_id):
    vacancy = Vacancy.query.get_or_404(vacancy_id)
    db.session.delete(vacancy)
    db.session.commit()
    return redirect(url_for('vacancy.list_vacancies'))

@vacancy_bp.route('/vacancies/create', methods=['GET', 'POST'])
@login_required
def create_vacancy():
    form = VacancyForm()
    if form.validate_on_submit():
        vacancy = Vacancy(
            title=form.title.data,
            description=form.description.data,
            employer_id=current_user.employer.id,
            employment_type=form.employment_type.data,
            responsibilities=form.responsibilities.data,
            requirements=form.requirements.data,
            conditions=form.conditions.data,
            key_skills=form.key_skills.data,
            specialty=form.specialty.data
        )
        db.session.add(vacancy)
        db.session.commit()
        return redirect(url_for('vacancy.list_vacancies'))
    return render_template('vacancy_creation.html', form=form)


@vacancy_bp.route('/vacancies/edit/<int:vacancy_id>', methods=['GET', 'POST'])
@login_required
def edit_vacancy(vacancy_id):
    vacancy = Vacancy.query.get_or_404(vacancy_id)
    form = VacancyForm(obj=vacancy)
    if form.validate_on_submit():
        vacancy.title = form.title.data
        vacancy.description = form.description.data
        db.session.commit()
        return redirect(url_for('vacancy.list_vacancies'))
    return render_template('vacancy_editing.html', form=form, vacancy=vacancy)


@vacancy_bp.route('/vacancies/view/<int:vacancy_id>', methods=['GET'])
@login_required
def view_vacancy(vacancy_id):
    vacancy = Vacancy.query.get_or_404(vacancy_id)
    return render_template('vacancy_review.html', vacancy=vacancy)


@application_bp.route('/apply/<int:vacancy_id>', methods=['POST'])
@login_required
def apply(vacancy_id):
    form = ApplicationForm()
    if form.validate_on_submit():
        application = Application(
            student_id=current_user.student.id, vacancy_id=vacancy_id)
        db.session.add(application)
        db.session.commit()
        return redirect(url_for('vacancy.view_vacancy', vacancy_id=vacancy_id))
    return redirect(url_for('vacancy.view_vacancy', vacancy_id=vacancy_id))
