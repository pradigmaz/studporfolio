from flask import Blueprint, render_template, redirect, url_for, request, current_app, jsonify, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import Application, ProjectFile, University, db, User, Student, Employer, RoleEnum, Project, Vacancy
from forms import ApplicationForm, EmployerSettingsForm, RegistrationFormStudent, RegistrationFormEmployer, LoginForm, StudentSettingsForm, UpdateEmailForm, UpdatePasswordForm, ProjectForm, VacancyForm
from werkzeug.utils import secure_filename
import os
import shutil
import logging



main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
profile_bp = Blueprint('profile', __name__)
settings_bp = Blueprint('settings', __name__)
project_bp = Blueprint('project', __name__)
vacancy_bp = Blueprint('vacancy', __name__)
filters_bp = Blueprint('filters', __name__)
application_bp = Blueprint('application', __name__)
search_bp = Blueprint('search', __name__)

CATEGORY_DISPLAY_NAMES = {
    'medicine': 'Медицина',
    'chemistry': 'Химия',
    'forestry': 'Лесное дело',
    'it': 'Информационные технологии',
    'engineering': 'Инженерия',
    'social_science': 'Социальные науки',
    'physics': 'Физика',
    'mathematics': 'Математика'
}

EMPLOYMENT_TYPE_DISPLAY_NAMES = {
    'full_time': 'Полная занятость',
    'part_time': 'Частичная занятость',
    'remote': 'Удалённая работа',
    'internship': 'Стажировка'
}

SPECIALTY_DISPLAY_NAMES = {
    'automotive': 'Автомобильный бизнес',
    'administrative': 'Административный персонал',
    'security': 'Безопасность',
    'management': 'Высший и средний менеджмент',
    'procurement': 'Закупки',
    'it': 'Информационные технологии',
    'marketing': 'Маркетинг, реклама, PR',
    'medicine': 'Медицина, фармацевтика',
    'science': 'Наука, образование',
    'sales': 'Продажи, обслуживание клиентов',
    'labor': 'Рабочий персонал',
    'retail': 'Розничная торговля',
    'agriculture': 'Сельское хозяйство',
    'tourism': 'Туризм, гостиницы, рестораны',
    'hr': 'Управление персоналом, тренинги',
    'finance': 'Финансы, бухгалтерия',
    'legal': 'Юристы'
}

@main_bp.route('/')
def index():
    logging.debug("Rendering index page")
    student_form = RegistrationFormStudent()
    employer_form = RegistrationFormEmployer()
    login_form = LoginForm()
    return render_template('index.html', student_form=student_form, employer_form=employer_form, login_form=login_form, RoleEnum=RoleEnum)


@auth_bp.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationFormStudent()
    if form.validate_on_submit():
        user = User(email=form.email.data, role=RoleEnum.STUDENT, phone=form.phone.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        student = Student(user_id=user.id, username=form.username.data, first_name=form.first_name.data,
                          last_name=form.last_name.data, middle_name=form.middle_name.data,
                          university_id=form.university.data)
        db.session.add(student)
        db.session.commit()
        user_folder = os.path.join(current_app.root_path, f'uploads/users/students/{student.username}')
        os.makedirs(user_folder, exist_ok=True)
        login_user(user)
        logging.info(f"Student {user.email} registered successfully")
        return redirect(url_for('profile.student_profile', username=student.username))
    logging.warning("Ошибка проверки формы регистрации студента")
    return render_template('index.html', student_form=form, employer_form=RegistrationFormEmployer(), login_form=LoginForm(), form=form, RoleEnum=RoleEnum)


@auth_bp.route('/register/employer', methods=['GET', 'POST'])
def register_employer():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationFormEmployer()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            logging.warning(f"Email {form.email.data} уже используется")
            return render_template('index.html', student_form=RegistrationFormStudent(), employer_form=form, login_form=LoginForm(), form=form, RoleEnum=RoleEnum, error='Email уже используется')
        
        user = User(email=form.email.data, role=RoleEnum.EMPLOYER, phone=form.phone.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        employer = Employer(
            user_id=user.id, company_name=form.company_name.data)
        db.session.add(employer)
        db.session.commit()
        user_folder = os.path.join(current_app.root_path, f'uploads/users/employers/{secure_filename(employer.company_name)}')
        os.makedirs(user_folder, exist_ok=True)
        login_user(user)
        logging.info(f"Employer {user.email} registered successfully")
        return redirect(url_for('profile.employer_profile', company_name=employer.company_name))
    logging.warning("Ошибка проверки формы регистрации работодателя")
    return render_template('index.html', student_form=RegistrationFormStudent(), employer_form=form, login_form=LoginForm(), form=form, RoleEnum=RoleEnum)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
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
                redirect_url = url_for('profile.student_profile', username=student.username)
            elif user.role == RoleEnum.EMPLOYER:
                employer = Employer.query.filter_by(user_id=user.id).first()
                redirect_url = url_for('profile.employer_profile', company_name=employer.company_name)
            else:
                redirect_url = url_for('main.index')

            return redirect(redirect_url)
        else:
            logging.warning(f"Неудачная попытка входа для {form.email.data}")
            return render_template('index.html', student_form=RegistrationFormStudent(), employer_form=RegistrationFormEmployer(), login_form=LoginForm(), error='Неверный email или пароль')
    return render_template('index.html', student_form=RegistrationFormStudent(), employer_form=RegistrationFormEmployer(), login_form=LoginForm(), error='Ошибка валидации формы')



@auth_bp.route('/logout')
@login_required
def logout():
    logging.info(f"User {current_user.email} logged out")
    logout_user()
    return redirect(url_for('main.index'))


@profile_bp.route('/profile/student/<username>')
@login_required
def student_profile(username):
    student = Student.query.filter_by(username=username).first_or_404()
    logging.debug(f"Отображение профиля студента {username}")
    return render_template('profile_students.html', student=student, RoleEnum=RoleEnum, category_display_names=CATEGORY_DISPLAY_NAMES)


@profile_bp.route('/profile/employer/<company_name>')
@login_required
def employer_profile(company_name):
    employer = Employer.query.filter_by(company_name=company_name).first_or_404()
    logging.debug(f"Отображение профиля работодателя {company_name}")
    return render_template('profile_employers.html', employer=employer, RoleEnum=RoleEnum)


@profile_bp.route('/students')
def students():
    logging.debug("Отображение страницы студентов")
    return render_template('presentation_students.html', student_form=RegistrationFormStudent(), employer_form=RegistrationFormEmployer(), login_form=LoginForm(), RoleEnum=RoleEnum)


@profile_bp.route('/employers')
def employers():
    logging.debug("Отображение страницы работодателей")
    return render_template('presentation_employers.html', employer_form=RegistrationFormEmployer(), login_form=LoginForm(), student_form=RegistrationFormStudent(), RoleEnum=RoleEnum)

# ПУТИ НАСТРОЕК

@settings_bp.route('/settings/student/<username>', methods=['GET', 'POST'])
@login_required
def student_settings(username):
    if current_user.role != RoleEnum.STUDENT:
        return redirect(url_for('main.index'))
    
    form = StudentSettingsForm(obj=current_user.student)
    form.phone.data = current_user.phone
    form.about.data = current_user.about  # Явно устанавливаем значение из модели пользователя
    form.university.choices = [(u.id, u.name) for u in University.query.all()]
    password_form = UpdatePasswordForm()
    email_form = UpdateEmailForm(current_email=current_user.email)

    logging.debug(f"Request method: {request.method}")
    if request.method == 'POST':
        logging.debug(f"Form data: {request.form}")
        logging.debug(f"About field in form data: {'about' in request.form}")
        logging.debug(f"University field in form data: {'university' in request.form}")
        logging.debug(f"University current ID: {current_user.student.university_id}")
        
        # Проверяем какая кнопка была нажата
        if form.delete_avatar.data:
            logging.debug("Processing delete avatar request")
            avatar_path = current_user.student.avatar_path
            if avatar_path and os.path.exists(avatar_path):
                os.remove(avatar_path)
                current_user.student.avatar_path = None
                db.session.commit()
            return redirect(url_for('settings.student_settings', username=username))
        
        # Обработка основной формы профиля
        elif 'profile_submit' in request.form or ('about' in request.form and 'university_submit' not in request.form):
            logging.debug("Processing profile form")
            # Заполняем форму данными из запроса для валидации
            form = StudentSettingsForm(request.form, obj=current_user.student)
            form.university.choices = [(u.id, u.name) for u in University.query.all()]
            
            if form.validate_on_submit():
                logging.debug("Student settings form validated successfully.")
                logging.debug(f"Form 'about' data: {form.about.data}")
                logging.debug(f"Current user 'about' before update: {current_user.about}")
                
                # Сохраняем текущее значение university_id перед обновлением
                current_university_id = current_user.student.university_id
                logging.debug(f"Current university_id before update: {current_university_id}")
                
                # Обновляем данные пользователя
                current_user.student.first_name = form.first_name.data
                current_user.student.last_name = form.last_name.data
                current_user.student.middle_name = form.middle_name.data
                
                # Проверяем, изменилось ли значение university в форме
                if 'university' in request.form and request.form['university']:
                    try:
                        university_id = int(request.form['university'])
                        university = University.query.get(university_id)
                        if university:
                            logging.debug(f"Updating university from form value: {university_id} ({university.name})")
                            current_user.student.university_id = university_id
                        else:
                            logging.warning(f"University with id {university_id} not found, keeping current value: {current_university_id}")
                    except ValueError:
                        logging.warning(f"Invalid university ID format: {request.form['university']}, keeping current value: {current_university_id}")
                else:
                    # Сохраняем текущее значение university_id
                    logging.debug(f"Preserving current university_id: {current_university_id}")
                
                current_user.phone = form.phone.data
                
                # Явно логируем обновление поля about
                logging.debug(f"Updating 'about' field from '{current_user.about}' to '{form.about.data}'")
                current_user.about = form.about.data
                
                logging.debug(f"Current user 'about' after assignment (before commit): {current_user.about}")
                
                # Попытка сохранения в базу данных
                try:
                    db.session.commit()
                    logging.debug("Database session committed for student settings.")
                    logging.debug(f"Verification after commit: User 'about' = {current_user.about}")
                    logging.debug(f"Verification after commit: University ID = {current_user.student.university_id}")
                    
                    # Проверка, что данные действительно сохранились
                    db.session.refresh(current_user)
                    logging.debug(f"After refresh: User 'about' = {current_user.about}")
                    logging.debug(f"After refresh: University ID = {current_user.student.university_id}")
                except Exception as e:
                    logging.error(f"Error during database commit: {str(e)}")
                    db.session.rollback()
                    flash('Произошла ошибка при сохранении данных', 'danger')
                    return redirect(url_for('settings.student_settings', username=username))
                
                # Обработка аватара, если он был загружен
                if form.avatar.data:
                    avatar_dir = os.path.join('static', 'uploads', 'users', 'students', username, 'avatars')
                    os.makedirs(avatar_dir, exist_ok=True)
                    avatar_path = os.path.join(avatar_dir, 'avatar.jpg')
                    form.avatar.data.save(avatar_path)
                    current_user.student.avatar_path = avatar_path
                    db.session.commit()
                
                # Добавляем флеш-сообщение для подтверждения
                flash('Настройки профиля успешно обновлены', 'success')
                return redirect(url_for('settings.student_settings', username=username))
            else:
                logging.debug(f"Form validation errors: {form.errors}")
                flash('Ошибка при обновлении профиля. Проверьте введенные данные.', 'danger')
        
        # Обработка формы изменения пароля
        elif 'password_submit' in request.form or 'current_password' in request.form:
            logging.debug("Processing password form")
            if password_form.validate_on_submit():
                # Обработка изменения пароля
                if current_user.check_password(password_form.current_password.data):
                    current_user.set_password(password_form.new_password.data)
                    db.session.commit()
                    flash('Ваш пароль был успешно изменен', 'success')
                else:
                    flash('Текущий пароль неверен', 'danger')
                return redirect(url_for('settings.student_settings', username=username))
            else:
                for field, errors in password_form.errors.items():
                    for error in errors:
                        flash(f'Ошибка в поле {field}: {error}', 'danger')
        
        # Обработка формы изменения email
        elif 'email_submit' in request.form or ('email' in request.form and 'current_email' in request.form):
            logging.debug("Processing email form")
            if email_form.validate_on_submit():
                current_user.email = email_form.email.data
                db.session.commit()
                flash('Ваш email был успешно изменен', 'success')
                return redirect(url_for('settings.student_settings', username=username))
            else:
                for field, errors in email_form.errors.items():
                    for error in errors:
                        flash(f'Ошибка в поле {field}: {error}', 'danger')
        
        # Обработка формы университета
        elif 'university_submit' in request.form:
            logging.debug("Processing university form")
            form.university.choices = [(u.id, u.name) for u in University.query.all()]
            if form.validate_on_submit():
                logging.debug(f"Updating university_id from university form: {form.university.data}")
                current_user.student.university_id = form.university.data
                db.session.commit()
                logging.debug(f"Verification after university commit: University ID = {current_user.student.university_id}")
                flash('Данные университета обновлены успешно', 'success')
                return redirect(url_for('settings.student_settings', username=username))
            else:
                logging.debug(f"University form validation errors: {form.errors}")
                flash('Ошибка при обновлении университета', 'danger')
    
    # Для GET запроса или после обработки формы
    return render_template('settings_students.html', form=form, password_form=password_form, email_form=email_form, RoleEnum=RoleEnum)



@settings_bp.route('/settings/employer/<company_name>', methods=['GET', 'POST'])
@login_required
def employer_settings(company_name):
    if current_user.role != RoleEnum.EMPLOYER:
        return redirect(url_for('main.index'))
    
    form = EmployerSettingsForm(obj=current_user.employer)
    password_form = UpdatePasswordForm()
    email_form = UpdateEmailForm(obj=current_user)

    if form.delete_avatar.data:
        avatar_path = current_user.employer.avatar_path
        if avatar_path and os.path.exists(avatar_path):
            os.remove(avatar_path)
            current_user.employer.avatar_path = None
            db.session.commit()
        return redirect(url_for('settings.employer_settings', company_name=company_name))

    if form.validate_on_submit():
        current_user.employer.company_name = form.company_name.data
        current_user.phone = form.phone.data
        current_user.about = form.about.data
        current_user.employer.address = form.address.data  # Добавить это поле
        if form.avatar.data:
            avatar_dir = os.path.join('static', 'uploads', 'users', 'employers', company_name, 'avatars')
            os.makedirs(avatar_dir, exist_ok=True)
            avatar_path = os.path.join(avatar_dir, 'avatar.jpg')
            form.avatar.data.save(avatar_path)
            current_user.employer.avatar_path = avatar_path
        db.session.commit()
        return redirect(url_for('settings.employer_settings', company_name=company_name))
    
    return render_template('settings_employers.html', form=form, password_form=password_form, email_form=email_form)





# ПУТИ ПРОЕКТОВ

@project_bp.route('/projects')
@login_required
def list_projects():
    projects = Project.query.filter_by(
        student_id=current_user.student.id).all()
    return render_template('project_list.html', projects=projects, RoleEnum=RoleEnum)


@project_bp.route('/projects/create', methods=['GET', 'POST'])
@login_required
def create_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            title=form.title.data,
            description=form.description.data,
            student_id=current_user.student.id,
            category=form.category.data,
            repository_url=form.repository_url.data
        )
        db.session.add(project)
        db.session.flush()

        project_folder = os.path.join(current_app.root_path, f'uploads/users/students/{current_user.student.username}/projects/{project.title}')
        os.makedirs(project_folder, exist_ok=True)

        if form.file.data:
            for uploaded_file in form.file.data:
                if uploaded_file:
                    filename = secure_filename(uploaded_file.filename)
                    file_path = os.path.join(project_folder, filename)
                    uploaded_file.save(file_path)
                    project_file = ProjectFile(file_path=file_path, project_id=project.id)
                    db.session.add(project_file)

        db.session.commit()
        return redirect(url_for('project.list_projects'))
    return render_template('project_creation.html', form=form)


@project_bp.route('/projects/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    form = ProjectForm(obj=project)
    form.existing_files.choices = [(file.id, file.file_path) for file in project.files]

    if form.validate_on_submit():
        if form.cancel.data:
            return redirect(url_for('project.list_projects'))

        project.title = form.title.data
        project.description = form.description.data
        project.category = form.category.data
        project.repository_url = form.repository_url.data

        if form.file.data:
            project_folder = os.path.join(current_app.root_path, f'uploads/users/students/{current_user.student.username}/projects/{project.title}')
            os.makedirs(project_folder, exist_ok=True)
            for uploaded_file in form.file.data:
                if uploaded_file:
                    filename = secure_filename(uploaded_file.filename)
                    file_path = os.path.join(project_folder, filename)
                    uploaded_file.save(file_path)
                    project_file = ProjectFile(file_path=file_path, project_id=project.id)
                    db.session.add(project_file)

        if form.add_new_files.data:
            project_folder = os.path.join(current_app.root_path, f'uploads/users/students/{current_user.student.username}/projects/{project.title}')
            os.makedirs(project_folder, exist_ok=True)
            for uploaded_file in form.add_new_files.data:
                if uploaded_file:
                    filename = secure_filename(uploaded_file.filename)
                    file_path = os.path.join(project_folder, filename)
                    uploaded_file.save(file_path)
                    project_file = ProjectFile(file_path=file_path, project_id=project.id)
                    db.session.add(project_file)

        if 'delete_selected' in request.form:
            files_to_delete = request.form.getlist('delete_files')
            for file_id in files_to_delete:
                file_to_delete = ProjectFile.query.get(file_id)
                if file_to_delete:
                    os.remove(file_to_delete.file_path)
                    db.session.delete(file_to_delete)

        db.session.commit()
        return redirect(url_for('project.edit_project', project_id=project.id))

    return render_template('project_editing.html', form=form, project=project, category_display_names=CATEGORY_DISPLAY_NAMES)


@project_bp.route('/projects/delete/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    project_folder = os.path.join(current_app.root_path, f'uploads/users/students/{project.student.username}/projects/{project.title}')
    
    db.session.delete(project)
    db.session.commit()
    
    if os.path.exists(project_folder):
        shutil.rmtree(project_folder)
    
    return redirect(url_for('project.list_projects'))

# ПУТИ ВАКАНСИЙ

@vacancy_bp.route('/vacancies')
@login_required
def list_vacancies():
    if current_user.role != RoleEnum.EMPLOYER:
        return redirect(url_for('main.index'))
    
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
        vacancy.employment_type = form.employment_type.data
        vacancy.responsibilities = form.responsibilities.data
        vacancy.requirements = form.requirements.data
        vacancy.conditions = form.conditions.data
        vacancy.key_skills = form.key_skills.data
        vacancy.specialty = form.specialty.data
        db.session.commit()
        return redirect(url_for('vacancy.list_vacancies'))
    return render_template('vacancy_editing.html', form=form, vacancy=vacancy)


@vacancy_bp.route('/vacancies/view/<int:vacancy_id>', methods=['GET'])
@login_required
def view_vacancy(vacancy_id):
    vacancy = Vacancy.query.get_or_404(vacancy_id)
    role = current_user.role if current_user.is_authenticated else None
    return render_template('search_vacancy.html', 
                           vacancy=vacancy, 
                           role=role, 
                           RoleEnum=RoleEnum, 
                           employment_type_display_names=EMPLOYMENT_TYPE_DISPLAY_NAMES, 
                           specialty_display_names=SPECIALTY_DISPLAY_NAMES)

# ПУТИ ОТКЛИКОВ

@application_bp.route('/apply/<int:vacancy_id>', methods=['POST'])
@login_required
def apply(vacancy_id):
    if current_user.role != RoleEnum.STUDENT:
        return redirect(url_for('main.index'))
    
    application = Application(student_id=current_user.student.id, vacancy_id=vacancy_id)
    db.session.add(application)
    db.session.commit()
    return redirect(url_for('vacancy.view_vacancy', vacancy_id=vacancy_id))

# ПУТИ ПОИСКА

@search_bp.route('/search')
def search_all():
    if not current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    query = request.args.get('query')
    category = request.args.get('category')
    specialty = request.args.get('specialty')
    include_inactive = request.args.get('include_inactive')

    students = []
    employers = []
    vacancies = []

    if query:
        if category in [None, 'students', '']:
            students = Student.query.filter(
                (Student.username.contains(query)) | 
                (Student.first_name.contains(query)) | 
                (Student.last_name.contains(query))
            ).all()
        if category in [None, 'employers', '']:
            employers = Employer.query.filter(
                Employer.company_name.contains(query)
            ).all()
        if category in [None, 'vacancies', '']:
            vacancies_query = Vacancy.query.filter(
                (Vacancy.title.contains(query)) | 
                (Vacancy.description.contains(query))
            )
            if specialty:
                vacancies_query = vacancies_query.filter_by(specialty=specialty)
            if include_inactive:
                vacancies_query = vacancies_query.filter_by(active=False)
            vacancies = vacancies_query.all()
    else:
        if category in [None, 'students', '']:
            students = Student.query.all()
        if category in [None, 'employers', '']:
            employers = Employer.query.all()
        if category in [None, 'vacancies', '']:
            vacancies_query = Vacancy.query
            if specialty:
                vacancies_query = vacancies_query.filter_by(specialty=specialty)
            vacancies = vacancies_query.all()

    role = current_user.role if current_user.is_authenticated else None
    specialties = VacancyForm().specialty.choices

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('search_results.html', students=students, employers=employers, vacancies=vacancies, category=category)

    return render_template('search.html', students=students, employers=employers, vacancies=vacancies, query=query, role=role, RoleEnum=RoleEnum, specialties=specialties, category=category)


@search_bp.route('/search/students')
def search_students():
    if not current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    query = request.args.get('query')
    students = Student.query.filter(Student.username.contains(query) | Student.first_name.contains(query) | Student.last_name.contains(query)).all()
    role = current_user.role if current_user.is_authenticated else None
    return render_template('search_student.html', students=students, query=query, role=role, RoleEnum=RoleEnum)


@search_bp.route('/search/employers')
def search_employers():
    if not current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    query = request.args.get('query')
    employers = Employer.query.filter(Employer.company_name.contains(query)).all()
    role = current_user.role if current_user.is_authenticated else None
    return render_template('search_employer.html', employers=employers, query=query, role=role, RoleEnum=RoleEnum)


@search_bp.route('/search/vacancies')
def search_vacancies():
    if not current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    query = request.args.get('query')
    vacancies = Vacancy.query.filter(Vacancy.title.contains(query) | Vacancy.description.contains(query)).all()
    role = current_user.role if current_user.is_authenticated else None
    return render_template('search_vacancy.html', vacancies=vacancies, query=query, role=role, RoleEnum=RoleEnum, employment_type_display_names=EMPLOYMENT_TYPE_DISPLAY_NAMES, 
                           specialty_display_names=SPECIALTY_DISPLAY_NAMES)


@search_bp.route('/search/view_vacancy/<int:vacancy_id>')
@login_required
def view_vacancy(vacancy_id):
    vacancy = Vacancy.query.get_or_404(vacancy_id)
    role = current_user.role if current_user.is_authenticated else None
    applicants = vacancy.get_applicants() if role == RoleEnum.EMPLOYER and current_user.employer.id == vacancy.employer_id else []
    is_applied = vacancy.is_applied_by_student(current_user.student.id) if role == RoleEnum.STUDENT else False
    return render_template('search_vacancy.html', 
                           vacancy=vacancy, 
                           role=role, 
                           RoleEnum=RoleEnum, 
                           applicants=applicants, 
                           is_applied=is_applied,
                           employment_type_display_names=EMPLOYMENT_TYPE_DISPLAY_NAMES, specialty_display_names=SPECIALTY_DISPLAY_NAMES)

@search_bp.route('/search/view_profiles/students/<username>')
@login_required
def view_student(username):
    student = Student.query.filter_by(username=username).first_or_404()
    role = current_user.role if current_user.is_authenticated else None
    return render_template('search_student.html', student=student, role=role, RoleEnum=RoleEnum, category_display_names=CATEGORY_DISPLAY_NAMES, specialty_display_names=SPECIALTY_DISPLAY_NAMES)

@search_bp.route('/search/view_profiles/employers/<company_name>')
@login_required
def view_employer(company_name):
    employer = Employer.query.filter_by(company_name=company_name).first_or_404()
    role = current_user.role if current_user.is_authenticated else None
    return render_template('search_employer.html', employer=employer, role=role, RoleEnum=RoleEnum)