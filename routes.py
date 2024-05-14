from forms import *
from flask_login import AnonymousUserMixin, current_user
from werkzeug.utils import secure_filename
from flask import abort, render_template, redirect, url_for, flash, request, send_from_directory
from forms import *
from models import *
from flask_login import login_user, login_required, current_user, logout_user
from main import app, db, get_user_avatar_folder, get_user_upload_folder, login_manager
from sqlalchemy import or_
import os
from functools import wraps
from urllib.parse import quote
from werkzeug.utils import secure_filename, safe_join

# ФУНКЦИИ


class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.username = 'Guest'
        self.role = 'anonymous'


@login_manager.user_loader
def load_user(user_id):
    user = Students.query.get(int(user_id))
    if user:
        return user
    user = Employers.query.get(int(user_id))
    if user:
        return user
    return Anonymous()


def check_and_save_file(file, allowed_extensions, user_folder):
    if file and allowed_file(file.filename, allowed_extensions):
        filename = secure_filename(file.filename)
        os.makedirs(user_folder, exist_ok=True)
        file_path = os.path.join(user_folder, filename)
        file.save(file_path)
        return filename
    else:
        flash("Недопустимый формат файла", "danger")
        return None


def save_avatar(file, username):
    if not file or not allowed_file(file.filename, app.config['ALLOWED_AVATAR_EXTENSIONS']):
        flash("Недопустимый формат файла", "danger")
        return None
    filename = secure_filename(file.filename)
    user_folder = get_user_avatar_folder(username)
    avatar_path = os.path.join(user_folder, filename)
    file.save(avatar_path)
    new_avatar_url = os.path.join(
        'avatars', secure_filename(username), filename)
    return new_avatar_url


def upload_avatar_students():
    file = request.files.get("avatar")
    if not file or file.filename == "":
        flash("Файл не выбран", "danger")
        return redirect(url_for("account", username=current_user.username))
    new_avatar_url = save_avatar(file, current_user.username)
    if new_avatar_url:
        current_user.avatar_url = new_avatar_url
        db.session.commit()
        flash("Аватар успешно загружен", "success")
    return redirect(url_for("account", username=current_user.username))


def upload_avatar_employers():
    file = request.files.get("avatar")
    if not file or file.filename == "":
        flash("Файл не выбран", "danger")
        return redirect(url_for("account_employer", username=current_user.username))
    new_avatar_url = save_avatar(file, current_user.username)
    if new_avatar_url:
        current_user.avatar_url = new_avatar_url
        db.session.commit()
        flash("Аватар успешно загружен", "success")
    return redirect(url_for("account_employers", username=current_user.username))

# ОБЩИЕ ПУТИ


@app.route("/", endpoint="index_home")
def index():
    avatar_filename = None
    if current_user.is_authenticated and current_user.avatar_url:
        avatar_filename = os.path.basename(current_user.avatar_url)
    employer_login_form = LoginFormEmployers()
    employer_register_form = RegistrationFormEmployers()
    student_login_form = LoginFormStudents()
    student_register_form = RegistrationFormStudents()
    return render_template("main.html", avatar_filename=avatar_filename, employer_login_form=employer_login_form, employer_register_form=employer_register_form, student_login_form=student_login_form, student_register_form=student_register_form) 


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        if current_user.role == 'student':
            return redirect(url_for('account', role='student', identifier=current_user.username))
        elif current_user.role == 'employer':
            return redirect(url_for('account', role='employer', identifier=current_user.company_name))

    student_form = RegistrationFormStudents()
    employer_form = RegistrationFormEmployers()

    if student_form.validate_on_submit():
        try:
            user = Students.register(
                surname=student_form.surname.data,
                first_name=student_form.first_name.data,
                middle_name=student_form.middle_name.data,
                username=student_form.username.data,
                phone_number=student_form.phone_number.data,
                email=student_form.email.data,
                password=student_form.password.data
            )
            user_folder = os.path.join(
                "user_folders", secure_filename(student_form.username.data))
            os.makedirs(user_folder, exist_ok=True)
            os.makedirs(os.path.join(user_folder, "files"), exist_ok=True)
            os.makedirs(os.path.join(user_folder, "avatars"), exist_ok=True)
            flash("Ваш аккаунт студента был создан! Теперь вы можете войти", "success")
            return redirect(url_for("login"))
        except ValueError as e:
            flash(str(e), "danger")

    if employer_form.validate_on_submit():
        try:
            employer = Employers.register(
                company_name=employer_form.company_name.data,
                contact_name=employer_form.contact_name.data,
                email=employer_form.email.data,
                phone_number=employer_form.phone_number.data,
                password=employer_form.password.data
            )
            flash(
                "Ваш аккаунт работодателя был создан! Теперь вы можете войти", "success")
            return redirect(url_for("login"))
        except ValueError as e:
            flash(str(e), "danger")

    return render_template("main.html", student_form=student_form, employer_form=employer_form)


@app.route("/login", methods=["GET", "POST"])
def login():
    student_form = LoginFormStudents()
    employer_form = LoginFormEmployers()

    if student_form.validate_on_submit():
        user = Students.query.filter(
            or_(
                Students.username == student_form.username_email.data,
                Students.email == student_form.username_email.data,
            )
        ).first()
        if user and user.check_password(student_form.password.data):
            login_user(user)
            flash("Вы успешно вошли в систему как студент!", "success")
            return redirect(url_for('account', role='student', identifier=user.username))

    if employer_form.validate_on_submit():
        user = Employers.query.filter_by(
            email=employer_form.email.data).first()
        if user and user.check_password(employer_form.password.data):
            login_user(user)
            flash("Вы успешно вошли в систему как работодатель!", "success")
            return redirect(url_for('account', role='employer', identifier=user.company_name))

    return render_template("main.html", student_form=student_form, employer_form=employer_form)


@app.route("/account/<role>/<identifier>")
@login_required
def account(role, identifier):
    if role == 'student':
        user = Students.query.filter_by(username=identifier).first_or_404()
        avatar_filename = os.path.basename(
            user.avatar_url) if user.avatar_url else None
        uploaded_files = PortfolioFile.query.filter_by(
            student_id=user.id).all()
        return render_template("account_students.html", user=user, avatar_filename=avatar_filename, uploaded_files=uploaded_files)
    elif role == 'employer':
        employer = Employers.query.filter_by(
            company_name=identifier).first_or_404()
        return render_template('account_employers.html', employer=employer)
    else:
        abort(404)  # Если роль не определена, возвращаем ошибку


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/employers')
def employers():
    return render_template('employers.html')


@app.route('/students')
def students():
    return render_template('students.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы успешно вышли из аккаунта", "success")
    return redirect(url_for("index_home"))


@app.route("/upload-avatar", methods=["POST"])
@login_required
def upload_avatar():
    if current_user.role == 'student':
        return upload_avatar_students()
    elif current_user.role == 'employer':
        return upload_avatar_employers()
    else:
        abort(403)


@app.route('/<role>/user_avatars/<username>/<filename>')
def user_avatar(role, username, filename):
    if role == 'student':
        directory = get_user_avatar_folder(username, 'student')
        default_filename = 'default_student_avatar.png'
    elif role == 'employer':
        directory = get_user_avatar_folder(username, 'employer')
        default_filename = 'default_employer_avatar.png'
    else:
        abort(404)
    if not os.path.isfile(os.path.join(directory, filename)):
        directory = app.config['STATIC_FOLDER']
        filename = default_filename
    return send_from_directory(directory, filename)


@app.route('/<role>/change_password', methods=['GET', 'POST'])
@login_required
def change_password(role):
    if role == 'student':
        if current_user.role != 'student':
            abort(403)
        form = ChangePasswordFormStudents()
    elif role == 'employer':
        if current_user.role != 'employer':
            abort(403)
        form = ChangePasswordFormEmployers()
    else:
        abort(404)

    if request.method == 'POST':
        if form.validate_on_submit():
            if current_user.check_password(form.current_password.data):
                current_user.set_password(form.new_password.data)
                db.session.commit()
                flash('Ваш пароль был успешно изменен.', 'success')
                return redirect(url_for('settings_'+role))
            else:
                flash('Неверный текущий пароль. Пожалуйста, попробуйте снова.', 'danger')
        return redirect(url_for('settings_'+role))
    else:
        return render_template('change_password.html', form=form)


@app.route("/<role>/settings", methods=["GET", "POST"])
@login_required
def settings(role):
    if role not in ['student', 'employer']:
        abort(403)

    if role == 'student':
        edit_profile_form = EditProfileFormStudents(obj=current_user)
        password_form = ChangePasswordFormStudents()
        avatar_form = ChangeAvatarFormStudents()
    else:
        edit_profile_form = EditProfileFormEmployers(obj=current_user)
        password_form = ChangePasswordFormEmployers()
        avatar_form = ChangeAvatarFormEmployers()

    if edit_profile_form.validate_on_submit():
        if role == 'student':
            if edit_profile_form.surname.data:
                current_user.surname = edit_profile_form.surname.data
            if edit_profile_form.first_name.data:
                current_user.first_name = edit_profile_form.first_name.data
            if edit_profile_form.middle_name.data:
                current_user.middle_name = edit_profile_form.middle_name.data
            if edit_profile_form.phone_number.data:
                current_user.phone_number = edit_profile_form.phone_number.data
            if edit_profile_form.about.data:
                current_user.about = edit_profile_form.about.data
        else:
            if edit_profile_form.company_name.data:
                current_user.company_name = edit_profile_form.company_name.data
            if edit_profile_form.contact_name.data:
                current_user.contact_name = edit_profile_form.contact_name.data
            if edit_profile_form.phone_number.data:
                current_user.phone_number = edit_profile_form.phone_number.data
            if edit_profile_form.about.data:
                current_user.about = edit_profile_form.about.data
        db.session.commit()
        flash('Ваши профильные данные были успешно обновлены.', 'success')

    if password_form.validate_on_submit():
        if current_user.check_password(password_form.current_password.data):
            current_user.set_password(password_form.new_password.data)
            db.session.commit()
            flash('Ваш пароль был успешно изменен.', 'success')
        else:
            flash('Текущий пароль неверен.', 'danger')

    if avatar_form.validate_on_submit():
        filename = secure_filename(avatar_form.avatar.data.filename)
        avatar_form.avatar.data.save(os.path.join(
            app.config['UPLOAD_FOLDER'], filename))
        current_user.avatar_filename = filename
        db.session.commit()
        flash('Ваш аватар был успешно обновлен.', 'success')

    if role == 'student':
        return render_template('settings_students.html', avatar_form=avatar_form, password_form=password_form, edit_profile_form=edit_profile_form)
    else:
        return render_template('settings_employers.html', avatar_form=avatar_form, password_form=password_form, edit_profile_form=edit_profile_form)


@app.route('/search', methods=['GET', 'POST'])
def search():
    base_template = "base.html"
    if current_user.is_authenticated:
        if current_user.role == 'student' or current_user.role == 'employer':
            if current_user.role == 'student':
                base_template = "base_students.html"
            elif current_user.role == 'employer':
                base_template = "base_employers.html"

            query = request.args.get('query', '')
            student_results = search_students(query)
            vacancy_results = search_vacancies(query)
            return render_template('search_results.html', base_template=base_template, query=query, student_results=student_results, vacancy_results=vacancy_results)
    else:
        query = request.args.get('query', '')
        vacancy_results = search_vacancies(query)
        return render_template('search_results.html', base_template=base_template, query=query, vacancy_results=vacancy_results)


def search_students(query):
    query_parts = query.split()
    if len(query_parts) == 1:
        students = Students.query.filter(
            (Students.first_name.ilike(f"%{query_parts[0]}%")) |
            (Students.surname.ilike(f"%{query_parts[0]}%")) |
            (Students.username.ilike(f"%{query_parts[0]}%"))
        ).all()
    elif len(query_parts) == 2:
        students = Students.query.filter(
            Students.first_name.ilike(f"%{query_parts[0]}%") &
            Students.surname.ilike(f"%{query_parts[1]}%")
        ).all()
    elif len(query_parts) == 3:
        students = Students.query.filter(
            Students.first_name.ilike(f"%{query_parts[0]}%") &
            Students.surname.ilike(f"%{query_parts[1]}%") &
            Students.middle_name.ilike(f"%{query_parts[2]}%")
        ).all()
    else:
        students = []
    return students


def search_vacancies(query):
    vacancies = Vacancy.query.filter(
        Vacancy.title.ilike(f"%{query}%") |
        Vacancy.description.ilike(f"%{query}%")
    ).all()
    return vacancies

# РАЗДЕЛ СТУДЕТОВ


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


@app.route('/student/portfolio_manager')
@login_required
def portfolio_manager():
    projects = current_user.projects
    return render_template('portfolio_manager.html', projects=projects)


@app.route('/student/edit_project/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    if current_user.role != 'student':
        abort(403)
    project = Project.query.get_or_404(project_id)
    form = ProjectFormStudents(obj=project)
    if form.validate_on_submit():
        project.title = form.title.data
        project.description = form.description.data
        project.field = form.field.data

        # Обработка загрузки новых файлов
        new_files = request.files.getlist('new_files')
        for file in new_files:
            if file:
                filename = secure_filename(file.filename)
                # Путь сохранения файла, включая директорию текущего пользователя
                user_upload_folder = os.path.join(
                    app.config['UPLOAD_FOLDER'], current_user.username)
                # Убедитесь, что папка существует
                os.makedirs(user_upload_folder, exist_ok=True)
                file_path = os.path.join(user_upload_folder, filename)
                file.save(file_path)
                # Добавление файла в базу данных без указания поддиректории пользователя
                new_project_file = ProjectFile(
                    filename=filename, project=project)
                db.session.add(new_project_file)

        db.session.commit()
        flash('Проект успешно обновлен.', 'success')
        return redirect(url_for('portfolio_manager'))
    return render_template('edit_project.html', form=form, project=project)


@app.route('/student/delete_project_file/<int:project_id>/<int:file_id>', methods=['POST'])
@login_required
def delete_project_file(project_id, file_id):
    if current_user.role != 'student':
        abort(403)
    project_file = ProjectFile.query.get_or_404(file_id)
    if project_file.project_id != project_id:
        abort(403)
    # Учет директории пользователя при формировании пути к файлу
    file_path = os.path.join(
        app.config['UPLOAD_FOLDER'], current_user.username, project_file.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.session.delete(project_file)
    db.session.commit()
    flash('Файл успешно удален.', 'success')
    return redirect(url_for('edit_project', project_id=project_id))


@app.route('/uploaded_file/<filename>')
@login_required
def uploaded_file(filename):
    user_upload_folder = get_user_upload_folder(current_user.username)
    return send_from_directory(user_upload_folder, filename)


@app.route('/student/delete_project/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.student_id != current_user.id:
        abort(403)

    # Удаление связанных файлов проекта из базы данных и файловой системы
    for project_file in project.files:
        file_path = os.path.join(
            get_user_upload_folder(current_user.username), secure_filename(project_file.filename))
        if os.path.exists(file_path):
            os.remove(file_path)  # Удаление файла с диска
        db.session.delete(project_file)

    db.session.delete(project)
    db.session.commit()
    flash('Проект и связанные файлы удалены', 'success')
    return redirect(url_for('portfolio_manager'))


@app.route('/student/project_draft', methods=['GET', 'POST'])
@login_required
def project_draft():
    if current_user.role != 'student':
        abort(403)
    form = ProjectFormStudents()
    if form.validate_on_submit():
        project = Project(
            title=form.title.data,
            description=form.description.data,
            field=form.field.data,
            student_id=current_user.id
        )
        db.session.add(project)
        db.session.commit()

        for file in form.files.data:
            filename = secure_filename(file.filename)
            user_upload_folder = get_user_upload_folder(current_user.username)
            file_path = os.path.join(user_upload_folder, filename)
            file.save(file_path)
            project_file = ProjectFile(filename=filename, project=project)
            db.session.add(project_file)
        db.session.commit()

        flash('Проект успешно создан!', 'success')
        return redirect(url_for('portfolio_manager'))
    return render_template('project_draft.html', form=form)

# РАЗДЕЛ РАБОТОДАТЕЛЯ


@app.route('/employer/settings', methods=['GET', 'POST'])
@login_required
def settings_employer():
    pass


@app.route('/employer/job_list')
@login_required
def job_list():
    return render_template('job_list.html')


@app.route('/employer/create_vacancy', methods=['GET', 'POST'])
@login_required
def create_vacancy():
    form = VacancyForm()
    if form.validate_on_submit():
        new_vacancy = Vacancy(
            title=form.title.data,
            description=form.description.data,
            is_active=form.is_active.data,
            employer_id=current_user.id,
            field=form.field.data  # Сохранение значения поля field
        )
        db.session.add(new_vacancy)
        db.session.commit()
        flash("Вакансия создана успешно!", "success")
        return redirect(url_for('job_list'))
    return render_template('create_vacancise.html', form=form)
