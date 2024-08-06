from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField, SelectField, SelectMultipleField, EmailField, IntegerField, TextAreaField, DecimalField
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
    

class InfluencerForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), email_validator])
    phone = StringField('Phone')
    mobile = StringField('Mobile')
    address = StringField('Address')
    category = SelectField('Category', choices=[('technology', 'Technology'), ('fashion', 'Fashion'), ('food', 'Food')], validators=[DataRequired()])
    niche = SelectMultipleField('Niche', choices=[('tech', 'Tech'), ('style', 'Style'), ('gourmet', 'Gourmet')], validators=[DataRequired()])
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    twitter_handle = StringField('Twitter Handle')
    twitter_followers = StringField('Twitter Followers')
    instagram_handle = StringField('Instagram Handle')
    instagram_followers = StringField('Instagram Followers')
    facebook_handle = StringField('Facebook Handle')
    facebook_followers = StringField('Facebook Followers')
    submit = SubmitField('Update Profile')


# class AdRequestForm(FlaskForm):
#     campaign_id = IntegerField('Campaign ID', validators=[DataRequired()])
#     influencer_id = IntegerField('Influencer ID', validators=[DataRequired()])
#     messages = TextAreaField('Messages', validators=[DataRequired()])
#     requirements = TextAreaField('Requirements', validators=[DataRequired()])
#     payment_amount = DecimalField('Payment Amount', validators=[DataRequired(), NumberRange(min=0)])
#     status = SelectField('Status', choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected')], validators=[DataRequired()])
#     submit = SubmitField('Submit')