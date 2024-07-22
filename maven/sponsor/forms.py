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

class SponsorForm(FlaskForm):
    full_name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), email_validator])
    phone = StringField('Phone')
    mobile = StringField('Mobile')
    address = StringField('Address')
    industry = SelectField('Industry', choices=[('technology', 'Technology'), ('fashion', 'Fashion'), ('food', 'Food')], validators=[DataRequired()])
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    website = StringField('Website')
    budget = StringField('Budget')
    submit = SubmitField('Update Profile')

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


