import os
from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
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


@influencer.route('/profile/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_profile(user_id):
    print("Delete profile route reached")

    influencer = Influencer.query.filter_by(user_id=user_id).first_or_404()
    if influencer.user_id != current_user.id:
        print("User does not have permission to delete this profile")
        abort(403)

    # Log the details of the influencer being deleted
    print(f"Deleting profile: {influencer}")

    
    # Delete profile picture from the filesystem if it's not the default one
    if influencer.profile_picture != 'default.jpg':
        picture_path = os.path.join('maven/static/profile_pics', influencer.profile_picture)
        if os.path.exists(picture_path):
            os.remove(picture_path)
            print(f"Profile picture {influencer.profile_picture} deleted from filesystem")
    
    db.session.delete(influencer)
    db.session.commit()
    print("Profile successfully deleted from database")
    flash('Your profile has been deleted!', 'success')
    return redirect(url_for('auth.logout'))




@influencer.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    if request.method == 'POST':
        print("Profile route received a POST request")

    influencer = Influencer.query.filter_by(user_id=user_id).first_or_404()
    form = InfluencerForm()
    
    if form.validate_on_submit():
        influencer.full_name = form.full_name.data
        influencer.email = form.email.data
        influencer.phone = form.phone.data
        influencer.mobile = form.mobile.data
        influencer.address = form.address.data
        influencer.category = form.category.data

        if form.niche.data:
            influencer.niche = ','.join(form.niche.data)

        influencer.twitter_handle = form.twitter_handle.data
        influencer.twitter_followers = form.twitter_followers.data
        influencer.instagram_handle = form.instagram_handle.data
        influencer.instagram_followers = form.instagram_followers.data
        influencer.facebook_handle = form.facebook_handle.data
        influencer.facebook_followers = form.facebook_followers.data

        # Handle file upload
        picture_file = form.profile_picture.data
        if picture_file:
            filename = secure_filename(picture_file.filename)
            picture_file.save(os.path.join('maven/static/profile_pics', filename))
            influencer.profile_picture = filename
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('influencer.profile', user_id=user_id))


    form.full_name.data = influencer.full_name
    form.email.data = influencer.email
    form.phone.data = influencer.phone
    form.mobile.data = influencer.mobile
    form.address.data = influencer.address
    form.category.data = influencer.category
    form.niche.data = influencer.niche.split(',') if influencer.niche else []
    form.twitter_handle.data = influencer.twitter_handle
    form.twitter_followers.data = influencer.twitter_followers
    form.instagram_handle.data = influencer.instagram_handle
    form.instagram_followers.data = influencer.instagram_followers
    form.facebook_handle.data = influencer.facebook_handle
    form.facebook_followers.data = influencer.facebook_followers

    return render_template('influencer/profile.html', title='Profile', form=form, influencer=influencer)



