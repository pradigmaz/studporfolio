from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, MultipleFileField
from wtforms import Form, IntegerField, SelectField, StringField, PasswordField, SubmitField, TelField, EmailField, FileField, BooleanField, TextAreaField, validators
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from models import *
import phonenumbers

def validate_uniqueness(model, field, message):
    def _validate(form, field):
        if model.query.filter_by(**{field.name: field.data}).first():
            raise ValidationError(message)
    return _validate


def validate_phone_number(self, field):
    if field.data:
        try:
            input_number = phonenumbers.parse(field.data, 'RU')
            if not phonenumbers.is_valid_number(input_number):
                raise ValidationError("Номер телефона недействителен")

            from routes import Students, Employers
            user = Students.query.filter_by(
                phone_number=field.data).first()
            if user:
                raise ValidationError(
                    "Этот номер телефона уже используется. Пожалуйста, введите другой.")
        except phonenumbers.NumberParseException:
            raise ValidationError("Неверный формат номера телефона")
                
# ФОРМЫ СТУДЕНТОВ

class RegistrationFormStudents(FlaskForm):
    surname = StringField("Фамилия", validators=[DataRequired()])
    first_name = StringField("Имя", validators=[DataRequired()])
    middle_name = StringField("Отчество", validators=[DataRequired()])
    username = StringField("Логин", validators=[DataRequired()])
    phone_number = TelField("Номер телефона", validators=[DataRequired(), validate_phone_number])
    email = EmailField("Электронная почта", validators=[DataRequired(), Email()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    confirm_password = PasswordField("Повторите пароль", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Регистрация")

    validate_email = validate_uniqueness(Students, 'email', "Этот email уже используется. Пожалуйста, введите другой.")
    validate_username = validate_uniqueness(Students, 'username', "Этот логин уже занят. Пожалуйста, выберите другой.")


class LoginFormStudents(FlaskForm):
    username_email = StringField("Логин или электронная почта", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Войти")


class ChangeAvatarFormStudents(FlaskForm):
    avatar = FileField("Выберите аватар", validators=[DataRequired()])
    submit_avatar = SubmitField("Загрузить аватар")


class ProjectFormStudents(FlaskForm):
    title = StringField("Название проекта", validators=[DataRequired()])
    description = TextAreaField("Описание проекта", validators=[DataRequired()])
    files = MultipleFileField("Файлы проекта", validators=[DataRequired()])
    submit = SubmitField("Создать проект")


class EditProfileFormStudents(FlaskForm):
    surname = StringField("Фамилия", validators=[DataRequired()])
    first_name = StringField("Имя", validators=[DataRequired()])
    middle_name = StringField("Отчество", validators=[DataRequired()])
    phone_number = TelField("Номер телефона", validators=[DataRequired(), validate_phone_number])
    about = TextAreaField('О себе', validators=[Length(max=1000)])
    submit = SubmitField('Сохранить изменения')


class ChangePasswordFormStudents(FlaskForm):
    current_password = PasswordField('Текущий пароль', validators=[DataRequired()])
    new_password = PasswordField('Новый пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Повторите новый пароль', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Изменить пароль')


# ФОРМЫ РАБОТОДАТЕЛЕЙ

class RegistrationFormEmployers(FlaskForm):
    company_name = StringField("Название компании", validators=[DataRequired(), Length(max=100)])
    contact_name = StringField("Контактное лицо", validators=[DataRequired(), Length(max=100)])
    email = EmailField("Электронная почта", validators=[DataRequired(), Email(), Length(max=120)])
    phone_number = TelField("Номер телефона", validators=[DataRequired(), validate_phone_number])
    password = PasswordField("Пароль", validators=[DataRequired(), Length(min=8, message='Пароль должен быть не менее %(min)d символов')])
    confirm_password = PasswordField("Повторите пароль", validators=[DataRequired(), EqualTo("password", message='Пароли должны совпадать')])
    submit = SubmitField("Зарегистрироваться")

    validate_email = validate_uniqueness(Employers, 'email', "Этот email уже используется. Пожалуйста, введите другой.")
    validate_username = validate_uniqueness(Employers, 'username', "Этот логин уже занят. Пожалуйста, выберите другой.")


class LoginFormEmployers(FlaskForm):
    email = EmailField("Электронная почта", validators=[DataRequired(), Email()])
    password = PasswordField("Пароль", validators=[DataRequired()])


class EditProfileFormEmployers(FlaskForm):
    company_name = StringField("Название компании", validators=[DataRequired(), Length(max=100)])
    contact_name = StringField("Контактное лицо", validators=[DataRequired(), Length(max=100)])
    phone_number = TelField("Номер телефона", validators=[DataRequired(), validate_phone_number])
    about = TextAreaField('О компании', validators=[Length(max=1000)])
    submit = SubmitField('Сохранить изменения')
    

class ChangePasswordFormEmployers(FlaskForm):
    current_password = PasswordField('Текущий пароль', validators=[DataRequired()])
    new_password = PasswordField('Новый пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Повторите новый пароль', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Изменить пароль')


class VacancyForm(FlaskForm):
    title = StringField("Название вакансии", validators=[DataRequired()])
    description = TextAreaField("Описание вакансии", validators=[DataRequired()])
    employment_type = StringField("Тип занятости", validators=[DataRequired()])
    responsibilities = TextAreaField("Обязанности", validators=[DataRequired()])
    requirements = TextAreaField("Требования", validators=[DataRequired()])
    conditions = TextAreaField("Условия работы", validators=[DataRequired()])
    key_skills = TextAreaField("Ключевые навыки", validators=[DataRequired()])
    is_active = BooleanField("Активна", default=True)
    employer_id = IntegerField("ID работодателя", validators=[DataRequired()])
    field = SelectField("Сфера деятельности", choices=[
        ('tech', 'Технологии'),
        ('health', 'Здравоохранение'),
        ('edu', 'Образование'),
        ('sport', 'Спорт'),
        ('art', 'Искусство'),
        ('science', 'Наука'),
        ('business', 'Бизнес'),
        ('psychology', 'Психология'),
        ('other', 'Другое')
    ], validators=[DataRequired()])
    submit = SubmitField("Создать вакансию")

class ChangeAvatarFormEmployers(FlaskForm):
    avatar = FileField("Выберите аватар", validators=[DataRequired()])
    submit_avatar = SubmitField("Загрузить аватар")
