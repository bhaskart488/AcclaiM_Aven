import os
from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import login_required, current_user
from maven import db
from maven.models import User, Influencer, AdRequest, Campaign, Sponsor
from maven.influencer.forms import InfluencerForm, CampaignSearchForm, NegotiateForm
# , AdRequestForm
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

    # Fetch the user object associated with the influencer
    user = User.query.get_or_404(user_id)

    # Delete profile picture from the filesystem if it's not the default one
    if influencer.profile_picture != 'default.jpg':
        picture_path = os.path.join('maven/static/profile_pics', influencer.profile_picture)
        if os.path.exists(picture_path):
            os.remove(picture_path)
            print(f"Profile picture {influencer.profile_picture} deleted from filesystem")
    
    # Delete the influencer profile
    db.session.delete(influencer)
    db.session.commit()
    print("Influencer profile successfully deleted from database")

    # Delete the user
    db.session.delete(user)
    db.session.commit()
    print("User account successfully deleted from database")

    flash('Your profile and account have been deleted!', 'success')
    return redirect(url_for('auth.logout'))



@influencer.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    if request.method == 'POST':
        print("Profile route received a POST request")

    if request.method == 'GET':
        print("Profile route received a GET request")

    form = InfluencerForm()

    print(f"Received user_id: {user_id}")

    try:
        influencer = Influencer.query.filter_by(user_id=user_id).first_or_404()
        print(f"Influencer found: {influencer}")
    except Exception as e:
        print(f"Error retrieving influencer: {e}")
        return render_template('errors/404.html'), 404

    # Check if the current user is the owner of the profile
    is_owner = influencer.user_id == current_user.id
    print(f"Is owner: {is_owner}")

    if not is_owner:
        # Pre-fill the form fields with influencer data
        form.full_name.data = influencer.full_name
        form.email.data = influencer.email
        form.phone.data = influencer.phone
        form.mobile.data = influencer.mobile
        form.address.data = influencer.address
        form.category.data = influencer.category
        if form.niche.data:
            influencer.niche = ','.join(form.niche.data)
        form.twitter_handle.data = influencer.twitter_handle
        form.twitter_followers.data = influencer.twitter_followers
        form.instagram_handle.data = influencer.instagram_handle
        form.instagram_followers.data = influencer.instagram_followers
        form.facebook_handle.data = influencer.facebook_handle
        form.facebook_followers.data = influencer.facebook_followers

    if form.validate_on_submit():
        print("Profile route received validate request")

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

        if form.profile_picture.data:
            picture_file = form.profile_picture.data
            filename = secure_filename(picture_file.filename)
            picture_path = os.path.join('maven/static/profile_pics', filename)
            picture_file.save(picture_path)
            influencer.profile_picture = filename

        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('influencer.profile', user_id=user_id))
    else:
        print(form.errors)

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

    # Render the profile template with different context based on whether the current user is the owner
    if is_owner:
        return render_template('influencer/profile.html', title='Profile', form=form, influencer=influencer)
    else:
        return render_template('influencer/profile_visitor.html', title='Profile', influencer=influencer)

#----------------------
# Ad-request routes



# @influencer.route('/ad_requests', methods=['GET'])
# @login_required
# def view_requests():
#     ad_requests = AdRequest.query.filter_by(influencer_id=current_user.id).all()
#     return render_template('influencer/view_requests.html', ad_requests=ad_requests)


@influencer.route('/ad_requests', methods=['GET'])
@login_required
def view_requests():
    influencer = Influencer.query.filter_by(user_id=current_user.id).first_or_404()
    ad_requests = AdRequest.query.filter_by(influencer_id=influencer.id).all()
    return render_template('influencer/view_requests.html', ad_requests=ad_requests)



@influencer.route('/ad_requests/<int:ad_request_id>/accept', methods=['POST', 'GET'])
@login_required
def accept_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    ad_request.status = 'Accepted'
    db.session.commit()
    flash('Ad Request accepted', 'success')
    return redirect(url_for('influencer.view_requests'))


@influencer.route('/ad_requests/<int:ad_request_id>/reject', methods=['POST', 'GET'])
@login_required
def reject_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    ad_request.status = 'Rejected'
    db.session.commit()
    flash('Ad Request rejected', 'danger')
    return redirect(url_for('influencer.view_requests'))


@influencer.route('/ad_requests/<int:ad_request_id>/negotiate', methods=['GET', 'POST'])
@login_required
def negotiate_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    form = NegotiateForm()
    if form.validate_on_submit():
        ad_request.offer_amount = form.offer_amount.data
        db.session.commit()
        flash('Negotiation submitted', 'success')
        return redirect(url_for('influencer.view_requests'))
    return render_template('influencer/negotiate.html', form=form, ad_request=ad_request)

# --------------------

# Search routes

# --------------------



@influencer.route('/search_campaigns', methods=['GET', 'POST'])
@login_required
def search_campaigns():
    form = CampaignSearchForm()
    campaigns = []
    if form.validate_on_submit():
        industry = form.industry.data
        # public_visibility = 'public'  # Assuming 'public' is a string; adjust if it's a different type
        campaigns = Campaign.query.join(Sponsor).filter(
            Sponsor.industry == industry,
            Campaign.visibility == 'public'
        ).all()

        print(campaigns)
    return render_template('influencer/search_results.html', form=form, campaigns=campaigns)

# edit the user_id, sponsor_id mismatch.