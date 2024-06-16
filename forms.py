from wtforms import BooleanField, MultipleFileField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, URL


class RegistrationFormStudent(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    middle_name = StringField('Отчество', validators=[Length(max=100)])
    email = StringField('Электронная почта', validators=[
                        DataRequired(), Email()])
    phone = StringField('Телефон', validators=[Length(max=20)])
    username = StringField('Имя пользователя', validators=[
                           DataRequired(), Length(max=100)])
    password = PasswordField('Пароль', validators=[
                             DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[
                                     DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')


class RegistrationFormEmployer(FlaskForm):
    company_name = StringField(
        'Название компании', validators=[DataRequired()])
    email = StringField('Электронная почта', validators=[
                        DataRequired(), Email()])
    phone = StringField('Телефон', validators=[Length(max=20)])
    password = PasswordField('Пароль', validators=[
                             DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[
                                     DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = StringField('Электронная почта', validators=[
                        DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class ProjectForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    file = MultipleFileField('Загрузить файлы проекта', validators=[FileAllowed(['pdf', 'docx', 'pptx'])])
    add_new_files = MultipleFileField('Добавить новые файлы к проекту', validators=[FileAllowed(['pdf', 'docx', 'pptx'])])
    existing_files = SelectField('Существующие файлы', choices=[], validators=[Optional()])

    category = SelectField('Категория', choices=[
        ('medicine', 'Медицина'),
        ('chemistry', 'Химия'),
        ('forestry', 'Лесное дело'),
        ('it', 'Информационные технологии'),
        ('engineering', 'Инженерия'),
        ('social_science', 'Социальные науки'),
        ('physics', 'Физика'),
        ('mathematics', 'Математика')
    ])
    repository_url = StringField('Ссылка на репозиторий проекта', validators=[Optional(), URL(message='Неверный URL')])
    submit = SubmitField('Создать проект')
    save = SubmitField('Сохранить изменения')
    cancel = SubmitField('Отмена')
    upload_files = SubmitField('Загрузить файлы')
    delete_files = SubmitField('Удалить выбранные файлы')
    delete_project = SubmitField('Удалить проект')


class ApplicationForm(FlaskForm):
    submit = SubmitField('Откликнуться')

class VacancyForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    employment_type = SelectField(
        'Тип занятости',
        choices=[
            ('full_time', 'Полная занятость'),
            ('part_time', 'Частичная занятость'),
            ('remote', 'Удалённая работа'),
            ('internship', 'Стажировка')
        ],
        validators=[DataRequired()]
    )
    responsibilities = TextAreaField('Обязанности', validators=[DataRequired()])
    requirements = TextAreaField('Требования', validators=[DataRequired()])
    conditions = TextAreaField('Условия работы', validators=[DataRequired()])
    key_skills = TextAreaField('Ключевые навыки', validators=[DataRequired()])
    specialty = SelectField('Сфера деятельности', choices=[
        ('automotive', 'Автомобильный бизнес'),
        ('administrative', 'Административный персонал'),
        ('security', 'Безопасность'),
        ('management', 'Высший и средний менеджмент'),
        ('procurement', 'Закупки'),
        ('it', 'Информационные технологии'),
        ('marketing', 'Маркетинг, реклама, PR'),
        ('medicine', 'Медицина, фармацевтика'),
        ('science', 'Наука, образование'),
        ('sales', 'Продажи, обслуживание клиентов'),
        ('labor', 'Рабочий персонал'),
        ('retail', 'Розничная торговля'),
        ('agriculture', 'Сельское хозяйство'),
        ('tourism', 'Туризм, гостиницы, рестораны'),
        ('hr', 'Управление персоналом, тренинги'),
        ('finance', 'Финансы, бухгалтерия'),
        ('legal', 'Юристы'),
    ], validators=[Optional()])
    submit = SubmitField('Создать вакансию')


class StudentSettingsForm(FlaskForm):
    first_name = StringField('Имя', validators=[Optional()])
    last_name = StringField('Фамилия', validators=[Optional()])
    middle_name = StringField('Отчество', validators=[Optional()])
    university = SelectField('Университет', choices=[], validators=[Optional()])
    phone = StringField('Телефон', validators=[Optional()])
    about = TextAreaField('О себе', validators=[Optional(), Length(max=500)])
    avatar = FileField('Аватар', validators=[FileAllowed(['jpg', 'png'])])
    delete_avatar = SubmitField('Удалить аватар')
    submit = SubmitField('Сохранить изменения')
    
    
class EmployerSettingsForm(FlaskForm):
    company_name = StringField('Название компании', validators=[Optional()])
    email = StringField('Электронная почта', validators=[Optional(), Email()])
    phone = StringField('Телефон', validators=[Optional()])
    about = TextAreaField('О компании', validators=[Optional()])
    avatar = FileField('Аватар', validators=[FileAllowed(['jpg', 'png'])])
    delete_avatar = SubmitField('Удалить аватар')
    submit = SubmitField('Сохранить изменения')

class UpdatePasswordForm(FlaskForm):
    current_password = PasswordField('Текущий пароль', validators=[DataRequired()])
    new_password = PasswordField('Новый пароль', validators=[
        DataRequired(), Length(min=6), EqualTo('confirm_new_password', message='Пароли должны совпадать')
    ])
    confirm_new_password = PasswordField('Подтвердите новый пароль', validators=[DataRequired()])
    submit = SubmitField('Изменить пароль')

class UpdateEmailForm(FlaskForm):
    current_email = StringField('Текущая электронная почта', render_kw={'readonly': True})
    email = StringField('Новая электронная почта', validators=[DataRequired(), Email()])
    submit = SubmitField('Изменить электронную почту')

class SearchForm(FlaskForm):
    query = StringField('Поиск...')
    category = SelectField('Категория', choices=[
        ('', 'Все категории'),
        ('students', 'Студенты'),
        ('employers', 'Работодатели'),
        ('vacancies', 'Вакансии')
    ])
    specialty = SelectField('Специальность', choices=[
        ('', 'Все специальности'),
        ('automotive', 'Автомобильный бизнес'),
        ('administrative', 'Административный персонал'),
        ('security', 'Безопасность'),
        ('management', 'Высший и средний менеджмент'),
        ('procurement', 'Закупки'),
        ('it', 'Информационные технологии'),
        ('marketing', 'Маркетинг, реклама, PR'),
        ('medicine', 'Медицина, фармацевтика'),
        ('science', 'Наука, образование'),
        ('sales', 'Продажи, обслуживание клиентов'),
        ('labor', 'Рабочий персонал'),
        ('retail', 'Розничная торговля'),
        ('agriculture', 'Сельское хозяйство'),
        ('tourism', 'Туризм, гостиницы, рестораны'),
        ('hr', 'Управление персоналом, тренинги'),
        ('finance', 'Финансы, бухгалтерия'),
        ('legal', 'Юристы'),
        ('other', 'Другое')
    ], validators=[Optional()])
    submit = SubmitField('Поиск')