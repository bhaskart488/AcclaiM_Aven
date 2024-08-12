from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, DecimalField
from wtforms.validators import DataRequired, Optional

class UserSearchForm(FlaskForm):
    industry = SelectField('Industry', choices=[('', 'Select Industry'), ('technology', 'Technology'), ('fashion', 'Fashion'), ('food', 'Food'), ('travel', 'Travel'), ('fitness', 'Fitness'), ('music', 'Music'), ('art', 'Art'), ('health', 'Health'), ('beauty', 'Beauty'), ('sports', 'Sports')], validators=[Optional()])
    category = SelectField('Category', choices=[('', 'Select Category'), ('national', 'National'), ('international', 'International'), ('local', 'Local'), ('regional', 'Regional'), ('global', 'Global')], validators=[Optional()])
    user_type = SelectField('User Type', choices=[('', 'Select Role'), ('sponsor', 'Sponsor'), ('influencer', 'Influencer')], validators=[Optional()])
    submit = SubmitField('Search')


class CampaignSearchForm(FlaskForm):
    visibility = SelectField('Visibility', choices=[('', 'Visibility'), ('public', 'Public'), ('private', 'Private')], validators=[Optional()])
    industry = SelectField('Industry', choices=[('', 'Select Industry'), ('technology', 'Technology'), ('fashion', 'Fashion'), ('food', 'Food'), ('travel', 'Travel'), ('fitness', 'Fitness'), ('music', 'Music'), ('art', 'Art'), ('health', 'Health'), ('beauty', 'Beauty'), ('sports', 'Sports')], validators=[Optional()])
    budget = DecimalField('Budget', places=2, validators=[Optional()])
    sponsor_name = StringField('Sponsor Name', validators=[Optional()])
    submit = SubmitField('Search')