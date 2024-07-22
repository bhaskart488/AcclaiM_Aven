from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField, SelectField, SelectMultipleField, EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
from flask_login import current_user
from maven.models import User
from email_validator import validate_email, EmailNotValidError

def email_validator(form, email):
    email = email.data
    try:
        valid = validate_email(email)
        email = valid.email
    except EmailNotValidError as e:
        raise ValidationError(str(e))

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), email_validator])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = RadioField('Role', choices=[('sponsor', 'Sponsor'), ('influencer', 'Influencer')], default='influencer', validators=[InputRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        if current_user.is_authenticated and username.data == current_user.username:
            return
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if current_user.is_authenticated and email.data == current_user.email:
            return
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')



