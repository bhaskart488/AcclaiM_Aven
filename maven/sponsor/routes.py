import os
from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
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

@sponsor.route('/sponsor/profile/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_profile(user_id):
    print("Delete profile route reached")

    sponsor = Sponsor.query.filter_by(user_id=user_id).first_or_404()
    if sponsor.user_id != current_user.id:
        print("User does not have permission to delete this profile")
        abort(403)

    # Log the details of the sponsor being deleted
    print(f"Deleting profile: {sponsor}")

    
    # Delete profile picture from the filesystem if it's not the default one
    if sponsor.profile_picture != 'default.jpg':
        picture_path = os.path.join('maven/static/profile_pics', sponsor.profile_picture)
        if os.path.exists(picture_path):
            os.remove(picture_path)
            print(f"Profile picture {sponsor.profile_picture} deleted from filesystem")
    
    db.session.delete(sponsor)
    db.session.commit()
    print("Profile successfully deleted from database")
    flash('Your profile has been deleted!', 'success')
    return redirect(url_for('auth.logout'))





@sponsor.route('/sponsor/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    sponsor = Sponsor.query.filter_by(user_id=user_id).first_or_404()
    form = SponsorForm()

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
