from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired

class UserSearchForm(FlaskForm):
    industry = StringField('Industry')
    niche = StringField('Niche')
    user_type = SelectField('User Type', choices=[('sponsor', 'Sponsor'), ('influencer', 'Influencer')])
    submit = SubmitField('Search')


class CampaignSearchForm(FlaskForm):
    name = StringField('Name')
    visibility = SelectField('Visibility', choices=[('public', 'Public'), ('private', 'Private')])
    submit = SubmitField('Search')