from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, DecimalField
from wtforms.validators import DataRequired, Optional

class UserSearchForm(FlaskForm):
    industry = StringField('Industry')
    niche = StringField('Niche')
    user_type = SelectField('User Type', choices=[('sponsor', 'Sponsor'), ('influencer', 'Influencer')])
    submit = SubmitField('Search')


class CampaignSearchForm(FlaskForm):
    visibility = SelectField('Visibility', choices=[('public', 'Public'), ('private', 'Private')])
    industry = SelectField('Industry', choices=[('', 'Select Industry'), ('technology', 'Technology'), ('fashion', 'Fashion'), ('food', 'Food'), ('travel', 'Travel'), ('fitness', 'Fitness'), ('music', 'Music'), ('art', 'Art'), ('health', 'Health'), ('beauty', 'Beauty'), ('sports', 'Sports')], validators=[Optional()])
    budget = DecimalField('Budget', places=2, validators=[Optional()])
    sponsor_name = StringField('Sponsor Name', validators=[Optional()])
    submit = SubmitField('Search')