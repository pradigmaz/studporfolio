from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegistrationFormStudent(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    middle_name = StringField('Отчество', validators=[Length(max=100)])
    email = StringField('Электронная почта', validators=[DataRequired(), Email()])
    phone = StringField('Телефон', validators=[Length(max=20)])
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(max=100)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

class RegistrationFormEmployer(FlaskForm):
    company_name = StringField('Название компании', validators=[DataRequired()])
    email = StringField('Электронная почта', validators=[DataRequired(), Email()])
    phone = StringField('Телефон', validators=[Length(max=20)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    email = StringField('Электронная почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class ProfileForm(FlaskForm):
    email = StringField('Электронная почта', validators=[DataRequired(), Email()])
    phone = StringField('Телефон', validators=[Length(max=20)])
    about = TextAreaField('О себе', validators=[Length(max=500)])
    avatar_url = StringField('URL аватара', validators=[Length(max=255)])
    submit = SubmitField('Обновить профиль')

class ProjectForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    submit = SubmitField('Создать проект')

class VacancyForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    submit = SubmitField('Создать вакансию')

