import os
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_required, current_user
from maven import db
from maven.models import Influencer
from maven.influencer.forms import InfluencerForm
from werkzeug.utils import secure_filename

influencer = Blueprint('influencer', __name__)

@influencer.route('/influencer-dashboard')
@login_required
def dashboard():
    return render_template('influencer/dashboard.html')



@influencer.route('/profile/<int:user_id>', methods=['GET', 'POST'])
def profile(user_id):
    print(f"Current User: {current_user}")  # Add this line to check user details
    form = InfluencerForm()
    influencer = Influencer.query.filter_by(user_id=user_id).first_or_404()

    if form.validate_on_submit():
        # Handle file upload
        picture_file = form.profile_picture.data
        if picture_file:
            filename = secure_filename(picture_file.filename)
            picture_file.save(os.path.join('maven/static/profile_pics', filename))
            influencer.profile_picture = filename

        # Update Influencer details
        influencer.full_name = form.full_name.data
        influencer.email = form.email.data
        influencer.phone = form.phone.data
        influencer.mobile = form.mobile.data
        influencer.address = form.address.data
        influencer.category = form.category.data

        if form.niche.data:
            influencer.niche = ','.join(form.niche.data)

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('influencer.profile', user_id=user_id))

    # Load existing influencer details
    form.full_name.data = influencer.full_name
    form.email.data = influencer.email
    form.phone.data = influencer.phone
    form.mobile.data = influencer.mobile
    form.address.data = influencer.address
    form.category.data = influencer.category
    form.niche.data = influencer.niche.split(',') if influencer.niche else []


    return render_template('influencer/profile.html', form=form, influencer=influencer)
