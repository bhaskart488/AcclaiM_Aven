import os
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from maven import db
from maven.models import Sponsor
from maven.sponsor.forms import SponsorForm
from werkzeug.utils import secure_filename


sponsor = Blueprint('sponsor', __name__)

@sponsor.route('/sponsor-dashboard')
@login_required
def dashboard():
    return render_template('sponsor/dashboard.html')

@sponsor.route('/profile/<int:user_id>', methods=['GET', 'POST'])
def profile(user_id):
    form = SponsorForm()
    sponsor = Sponsor.query.filter_by(user_id=user_id).first_or_404()

    if form.validate_on_submit():
        # Update Sponsor details
        sponsor.full_name = form.full_name.data
        sponsor.email = form.email.data
        sponsor.phone = form.phone.data
        sponsor.mobile = form.mobile.data
        sponsor.address = form.address.data
        sponsor.industry = form.industry.data

        sponsor.website = form.website.data
        sponsor.budget = form.budget.data
        
        # Handle file upload
        picture_file = form.profile_picture.data
        if picture_file:
            filename = secure_filename(picture_file.filename)
            picture_file.save(os.path.join('maven/static/profile_pics', filename))
            sponsor.profile_picture = filename

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('sponsor.profile', user_id=user_id))

    # Load existing sponsor details
    form.full_name.data = sponsor.full_name
    form.email.data = sponsor.email
    form.phone.data = sponsor.phone
    form.mobile.data = sponsor.mobile
    form.budget.data = sponsor.budget
    form.address.data = sponsor.address
    form.industry.data = sponsor.industry
    form.website.data = sponsor.website
    form.budget.data = sponsor.budget

    return render_template('sponsor/profile.html', title='Profile', form=form, sponsor=sponsor)


# # Example in maven/sponsor/routes.py
# @auth.route('/campaigns', methods=['GET', 'POST'])
# @login_required
# def manage_campaigns():
#     if request.method == 'POST':
#         data = {
#             'name': request.form.get('name'),
#             'description': request.form.get('description')
#         }
#         response = requests.post(f'{API_URL}/campaign', json=data)
#         if response.status_code == 201:
#             flash('Campaign created successfully', 'success')
#         else:
#             flash('Failed to create campaign', 'danger')
#     campaigns = requests.get(f'{API_URL}/campaign').json()
#     return render_template('sponsor/campaigns.html', campaigns=campaigns)
