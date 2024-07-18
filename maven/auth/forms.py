from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, FloatField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
from flask_login import current_user
from maven.models import User
from email_validator import validate_email, EmailNotValidError

def email_validator(form, email):
    email = email.data
    try:
        # Validate.
        valid = validate_email(email)
        # Update with the normalized form.
        email = valid.email
    except EmailNotValidError as e:
        # email is not valid, raise a validation error.
        raise ValidationError(str(e))

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), email_validator])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = RadioField('Role', choices=[('sponsor', 'Sponsor'), ('influencer', 'Influencer')], default='influencer', validators=[InputRequired()])
    remember = BooleanField('Remember me')
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

class SponsorForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired()])
    industry = StringField('Industry', validators=[DataRequired()])
    budget = FloatField('Budget', validators=[DataRequired()])
    picture = FileField('Update profile picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Complete Registration')

class InfluencerForm(FlaskForm):
    category = StringField('Category', validators=[DataRequired()])
    niche = StringField('Niche', validators=[DataRequired()])
    reach = StringField('Reach', validators=[DataRequired()])
    picture = FileField('Update profile picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Complete Registration')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), email_validator])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')
