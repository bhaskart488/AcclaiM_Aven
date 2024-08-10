import os
from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import login_required, current_user
from maven import db
from maven.models import User, Influencer, AdRequest, Campaign, Sponsor, Notification
from maven.influencer.forms import InfluencerForm, CampaignSearchForm, NegotiateForm, UpdateCompletionStatusForm
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
    print(current_user.id)

    ad_requests = AdRequest.query.filter_by(influencer_id=Influencer.query.filter_by(user_id=current_user.id).first().user_id).all()
    ad_requests = AdRequest.query.filter_by(influencer_id=Influencer.query.filter_by(user_id=current_user.id).first().user_id).all()
    campaign_ids = [ad_request.campaign_id for ad_request in ad_requests]
    campaigns = Campaign.query.filter(Campaign.id.in_(campaign_ids)).all()

    return render_template('influencer/view_requests.html', ad_requests=ad_requests, campaigns=campaigns)



@influencer.route('/ad_requests/<int:ad_request_id>/accept', methods=['POST', 'GET'])
@login_required
def accept_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    ad_request.status = 'Accepted'
    db.session.commit()

    # Create a notification
    campaign = Campaign.query.get(ad_request.campaign_id)
    # influencer = Influencer.query.get(ad_request.influencer_id)
    influencer = Influencer.query.filter_by(user_id=ad_request.influencer_id).first()

    notification = Notification(
        user_id=campaign.sponsor_id,
        message=f'Ad request {ad_request_id} for {campaign.name} has been accepted by {influencer.full_name} for INR {ad_request.offer_amount}.'
    )
    db.session.add(notification)
    db.session.commit()


    flash('Ad Request accepted', 'success')
    return redirect(url_for('influencer.view_requests'))


@influencer.route('/ad_requests/<int:ad_request_id>/reject', methods=['POST', 'GET'])
@login_required
def reject_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    ad_request.status = 'Rejected'
    db.session.commit()


    # Create a notification
    campaign = Campaign.query.get(ad_request.campaign_id)
    # influencer = Influencer.query.get(ad_request.influencer_id)
    influencer = Influencer.query.filter_by(user_id=ad_request.influencer_id).first()

    notification = Notification(
        user_id=campaign.sponsor_id,
        message=f'Ad request {ad_request_id} has been rejected by {influencer.full_name} for INR {ad_request.offer_amount}.'
    )
    db.session.add(notification)
    db.session.commit()

    flash('Ad Request rejected', 'danger')
    return redirect(url_for('influencer.view_requests'))


#negotiate route

@influencer.route('/ad_requests/<int:ad_request_id>/negotiate', methods=['GET', 'POST'])
@login_required
def negotiate_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    form = NegotiateForm()
    if form.validate_on_submit():
        ad_request.offer_amount = form.offer_amount.data
        ad_request.messages = form.messages.data  # Save the messages data
        ad_request.status = 'Negotiation'
        db.session.commit()
        
        # Create a notification
        campaign = Campaign.query.get(ad_request.campaign_id)
        # influencer = Influencer.query.get(ad_request.influencer_id)
        influencer = Influencer.query.filter_by(user_id=ad_request.influencer_id).first()


        notification = Notification(
            user_id=campaign.sponsor_id,
            message=f'Ad request {ad_request_id} has a negotiation request for INR {form.offer_amount.data} by {influencer.full_name}.'
        )
        db.session.add(notification)
        db.session.commit()
        
        flash('Negotiation submitted', 'success')
        return redirect(url_for('influencer.view_requests'))
    else:
        form.offer_amount.data = ad_request.offer_amount  # Prefill the offer_amount data
        form.messages.data = ad_request.messages  # Prefill the messages data
    return render_template('influencer/negotiate.html', form=form, ad_request=ad_request)


@influencer.route('/ad_request/<int:ad_request_id>')
def view_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    campaign = Campaign.query.get(ad_request.campaign_id)
    influencer = Influencer.query.filter_by(user_id=ad_request.influencer_id).first()

    if influencer.user_id != current_user.id:
        flash('You do not have permission to view this ad request', 'danger')
        return redirect(url_for('influencer.view_requests'))

    form = UpdateCompletionStatusForm()
    form.completion_status.data = ad_request.completion_status  # Prepopulate the completion status field

    return render_template('influencer/view_ad_request.html', ad_request=ad_request, campaign=campaign, influencer=influencer, form=form)


@influencer.route('/influencer/ad_request/<int:ad_request_id>/update_status', methods=['POST'])
@login_required
def update_completion_status(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if ad_request.influencer_id != current_user.id:
        flash('You do not have permission to update this ad request', 'danger')
        return redirect(url_for('influencer.view_requests'))

    form = UpdateCompletionStatusForm()
    if form.validate_on_submit():
        # Log the form data for debugging
        print(f"Form Data: {form.completion_status.data}")

        ad_request.completion_status = form.completion_status.data
        try:
            db.session.commit()
            flash('Ad request status updated successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Failed to update completion status: {str(e)}', 'danger')
    else:
        flash('Failed to update completion status', 'danger')

    return redirect(url_for('influencer.view_requests'))


#notification route

@influencer.route('/notifications')
def view_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.timestamp.desc()).all()
    return render_template('main/notifications.html', notifications=notifications)


@influencer.route('/notifications/read/<int:notification_id>', methods=['POST'])
def mark_notification_as_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        abort(403)  # Forbidden
    notification.is_read = True
    db.session.commit()
    return redirect(url_for('main.notifications'))

@influencer.route('/notifications/delete/<int:notification_id>', methods=['POST'])
@login_required
def delete_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        abort(403)  # Forbidden
    db.session.delete(notification)
    db.session.commit()
    return redirect(url_for('main.notifications'))

# --------------------

# Search routes

# --------------------


@influencer.route('/influencer/search_campaigns', methods=['GET', 'POST'])
@login_required
def search_campaigns():
    form = CampaignSearchForm()
    campaigns = []
    industry = None
    budget = None
    sponsor_name = None
    
    if form.validate_on_submit():
        industry = form.industry.data
        budget = form.budget.data
        sponsor_name = form.sponsor_name.data
        query = Campaign.query.join(Sponsor, Sponsor.user_id == Campaign.sponsor_id).filter(
            Campaign.visibility == 'public'
        )
        if industry:
            query = query.filter(Sponsor.industry == industry)
        if budget:
            query = query.filter(Campaign.budget <= budget)
        if sponsor_name:
            query = query.filter(Sponsor.full_name.ilike(f'%{sponsor_name}%'))
        campaigns = query.add_columns(Sponsor.full_name, Sponsor.website).all()
    
    return render_template('influencer/search_results.html', form=form, campaigns=campaigns, industry=industry, budget=budget, sponsor_name=sponsor_name)

# edit the user_id, sponsor_id mismatch.


# analytics
from flask import render_template
from flask_login import current_user
from maven.models import AdRequest, Campaign
from maven import db

@influencer.route('/influencer/analytics')
@login_required
def influencer_analytics():
    influencer_id = current_user.id

    # Query for total ad requests
    total_ad_requests = AdRequest.query.filter_by(influencer_id=influencer_id).count()

    # Query for complete and incomplete ad requests
    complete_ad_requests = AdRequest.query.filter_by(influencer_id=influencer_id, completion_status='Complete').count()
    incomplete_ad_requests = AdRequest.query.filter_by(influencer_id=influencer_id, completion_status='Incomplete').count()

    # Query for ad request statuses
    ad_request_statuses = db.session.query(
        AdRequest.status, db.func.count(AdRequest.id)
    ).filter_by(influencer_id=influencer_id).group_by(AdRequest.status).all()

    # Query for ad request completion status
    ad_request_completion_status = db.session.query(
        AdRequest.completion_status, db.func.count(AdRequest.id)
    ).filter_by(influencer_id=influencer_id).group_by(AdRequest.completion_status).all()

    # Query for offer amount per ad request
    offer_amounts = db.session.query(
        AdRequest.id, AdRequest.offer_amount
    ).filter_by(influencer_id=influencer_id).all()

    # Query for earnings from each campaign
    campaign_earnings = db.session.query(
        Campaign.name, db.func.sum(AdRequest.offer_amount)
    ).join(AdRequest).filter(AdRequest.influencer_id == influencer_id).group_by(Campaign.name).all()

    # Calculate total earnings
    total_earnings = sum([earning[1] for earning in campaign_earnings])

    data = {

        'total_ad_requests': total_ad_requests,
        'complete_ad_requests': complete_ad_requests,
        'incomplete_ad_requests': incomplete_ad_requests,
        'ad_request_statuses': list(ad_request_statuses),
        'ad_request_completion_status': list(ad_request_completion_status),
        'offer_amounts': list(offer_amounts),
        'campaign_earnings': list(campaign_earnings),
        'total_earnings': total_earnings
    }

    return render_template('influencer/analytics.html', data=data)