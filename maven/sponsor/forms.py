from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField, DecimalField, TextAreaField, IntegerField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired, NumberRange
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
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
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


class CampaignForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    budget = IntegerField('Budget', validators=[DataRequired()])
    visibility = SelectField('Visibility', choices=[('public', 'Public'), ('private', 'Private')], validators=[DataRequired()])
    goals = StringField('Goals')


# class AdRequestForm(FlaskForm):
#     campaign_id = IntegerField('Campaign ID', validators=[DataRequired()])
#     influencer_id = IntegerField('Influencer ID', validators=[DataRequired()])
#     messages = TextAreaField('Messages', validators=[DataRequired()])
#     requirements = TextAreaField('Requirements', validators=[DataRequired()])
#     payment_amount = DecimalField('Payment Amount', validators=[DataRequired(), NumberRange(min=0)])
#     status = SelectField('Status', choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected')], validators=[DataRequired()])
#     submit = SubmitField('Submit')