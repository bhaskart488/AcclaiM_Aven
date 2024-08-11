from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField, DecimalField, TextAreaField, IntegerField, DateField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired, NumberRange, Optional, Regexp
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
    industry = SelectField('Industry', choices=[('technology', 'Technology'), ('fashion', 'Fashion'), ('food', 'Food'), ('travel', 'Travel'), ('fitness', 'Fitness'), ('music', 'Music'), ('art', 'Art'), ('health', 'Health'), ('beauty', 'Beauty'), ('sports', 'Sports')], validators=[DataRequired()])
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


class AdRequestForm(FlaskForm):
    campaign_id = IntegerField('Campaign', validators=[DataRequired()])
    influencer_id = IntegerField('Influencer', validators=[DataRequired()])
    messages = TextAreaField('Messages', validators=[DataRequired()])
    requirements = TextAreaField('Requirements', validators=[DataRequired()])
    offer_amount = DecimalField('Offer Amount', validators=[DataRequired(), NumberRange(min=0)])
    status = SelectField('Status', choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected')], validators=[DataRequired()])
    submit = SubmitField('Create Ad Request')
    

    def __init__(self, *args, **kwargs):
        super(AdRequestForm, self).__init__(*args, **kwargs)
        if 'campaign_id' in kwargs:
            self.campaign_id.data = kwargs['campaign_id']


class AdRequestEditForm(FlaskForm):
    campaign_id = HiddenField('Campaign ID')
    influencer_id = HiddenField('Influencer ID')
    messages = TextAreaField('Messages', validators=[DataRequired()])
    requirements = TextAreaField('Requirements', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected'), ('Negotiation', 'Negotiation')], validators=[DataRequired()])
    offer_amount = DecimalField('Offer Amount', validators=[DataRequired()])


class NegotiateForm(FlaskForm):
    offer_amount = DecimalField('Offer Amount', validators=[DataRequired()])
    submit = SubmitField('Submit')


class InfluencerSearchForm(FlaskForm):
    category = SelectField('Category', choices=[('', 'Select Category'), ('national', 'National'), ('international', 'International'), ('local', 'Local'), ('regional', 'Regional'), ('global', 'Global')], validators=[Optional()])
    niche = SelectField('Niche', choices=[('', 'Select Niche'), ('technology', 'Technology'), ('fashion', 'Fashion'), ('food', 'Food'), ('travel', 'Travel'), ('fitness', 'Fitness'), ('music', 'Music'), ('art', 'Art'), ('health', 'Health'), ('beauty', 'Beauty'), ('sports', 'Sports')], validators=[Optional()])
    search_text = StringField('Name', validators=[Optional()])
    submit = SubmitField('Search')


# Payment Form

# class PaymentForm(FlaskForm):
#     card_number = StringField('Card Number', validators=[DataRequired()])
#     card_holder_name = StringField('Card Holder Name', validators=[DataRequired()])
#     expiry_date = StringField('Expiry Date (MM/YY)', validators=[DataRequired()])
#     cvv = StringField('CVV', validators=[DataRequired()])
#     amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0)])
#     submit = SubmitField('Pay')

class PaymentForm(FlaskForm):
    card_number = StringField('Card Number', validators=[
        DataRequired(),
        Regexp(r'^\d{16}$', message="Card number must be 16 digits"),
        Length(min=16, max=16, message="Card number must be 16 digits")
    ])
    card_holder_name = StringField('Card Holder Name', validators=[DataRequired()])
    expiry_date = StringField('Expiry Date (MMYY)', validators=[
        DataRequired(),
        Regexp(r'^\d{4}$', message="Expiry date must be 4 digits in MMYY format"),
        Length(min=4, max=4, message="Expiry date must be 4 digits in MMYY format")
    ])
    cvv = StringField('CVV', validators=[
        DataRequired(),
        Regexp(r'^\d{3}$', message="CVV must be 3 digits"),
        Length(min=3, max=3, message="CVV must be 3 digits")
    ])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Pay')