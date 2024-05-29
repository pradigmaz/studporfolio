from wtforms import BooleanField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length


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
    file = FileField('Файл проекта', validators=[
                     FileAllowed(['pdf', 'docx', 'txt'])])
    submit = SubmitField('Создать проект')


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
    responsibilities = TextAreaField(
        'Обязанности', validators=[DataRequired()])
    requirements = TextAreaField('Требования', validators=[DataRequired()])
    conditions = TextAreaField('Условия работы', validators=[DataRequired()])
    key_skills = TextAreaField('Ключевые навыки', validators=[DataRequired()])
    specialty = SelectField(
        'Сфера деятельности',
        choices=[
            ('automotive', 'Автомобильный бизнес'),
            ('administrative', 'Административный персонал'),
            ('security', 'Безопасность'),
            ('management', 'Высший и средний менеджмент'),
            ('extraction', 'Добыча сырья'),
            ('domestic', 'Домашний, обслуживающий персонал'),
            ('procurement', 'Закупки'),
            ('it', 'Информационные технологии'),
            ('art', 'Искусство, развлечения, массмедиа'),
            ('marketing', 'Маркетинг, реклама, PR'),
            ('medicine', 'Медицина, фармацевтика'),
            ('science', 'Наука, образование'),
            ('sales', 'Продажи, обслуживание клиентов'),
            ('production', 'Производство, сервисное обслуживание'),
            ('labor', 'Рабочий персонал'),
            ('retail', 'Розничная торговля'),
            ('agriculture', 'Сельское хозяйство'),
            ('sports', 'Спортивные клубы, фитнес, салоны красоты'),
            ('strategy', 'Стратегия, инвестиции, консалтинг'),
            ('insurance', 'Страхование'),
            ('construction', 'Строительство, недвижимость'),
            ('transport', 'Транспорт, логистика, перевозки'),
            ('tourism', 'Туризм, гостиницы, рестораны'),
            ('hr', 'Управление персоналом, тренинги'),
            ('finance', 'Финансы, бухгалтерия'),
            ('legal', 'Юристы'),
            ('other', 'Другое')
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('Создать вакансию')


class UpdateAvatarForm(FlaskForm):
    avatar = FileField('Аватар', validators=[
                       FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Обновить аватар')


class UpdateEmailForm(FlaskForm):
    email = StringField('Электронная почта', validators=[
                        DataRequired(), Email()])
    submit = SubmitField('Обновить электронную почту')


class UpdatePasswordForm(FlaskForm):
    current_password = PasswordField(
        'Текущий пароль', validators=[DataRequired()])
    new_password = PasswordField('Новый пароль', validators=[
                                 DataRequired(), Length(min=6)])
    confirm_new_password = PasswordField('Подтвердите новый пароль', validators=[
                                         DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Обновить пароль')
