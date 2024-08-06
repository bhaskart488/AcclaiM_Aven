import os
from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import login_user, current_user, logout_user, login_required
from maven import db
from maven.models import User, Sponsor, Campaign, AdRequest
from maven.sponsor.forms import SponsorForm, CampaignForm
# AdRequestForm
from werkzeug.utils import secure_filename
import requests

sponsor = Blueprint('sponsor', __name__)


@sponsor.route('/sponsor-dashboard')
@login_required
def dashboard():
    return render_template('sponsor/dashboard.html', title='Sponsor')

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

    # Fetch the user object associated with the influencer
    user = User.query.get_or_404(user_id)
    
    # Delete profile picture from the filesystem if it's not the default one
    if sponsor.profile_picture != 'default.jpg':
        picture_path = os.path.join('maven/static/profile_pics', sponsor.profile_picture)
        if os.path.exists(picture_path):
            os.remove(picture_path)
            print(f"Profile picture {sponsor.profile_picture} deleted from filesystem")
    
    db.session.delete(sponsor)
    db.session.commit()
    print("Sponsor Profile successfully deleted from database")

    # Delete the user
    db.session.delete(user)
    db.session.commit()
    print("User account successfully deleted from database")

    flash('Your profile and account have been deleted!', 'success')
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



API_URL = 'http://localhost:5000/api'  # Replace with the actual API URL


# Campaign Management Routes

@sponsor.route('/campaigns', methods=['GET', 'POST'])
@login_required
def manage_campaigns():
    form=CampaignForm()
    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'start_date': request.form.get('start_date'),
            'end_date': request.form.get('end_date'),
            'budget': request.form.get('budget'),
            'visibility': request.form.get('visibility'),
            'goals': request.form.get('goals'),
            'sponsor_id': current_user.id  # Use the current user's ID
        }
        response = requests.post(f'{API_URL}/campaigns', json=data)
        if response.status_code == 201:
            flash('Campaign created successfully', 'success')
        else:
            flash('Failed to create campaign', 'danger')
        return redirect(url_for('sponsor.manage_campaigns'))  # Redirect to avoid form resubmission
    
    response = requests.get(f'{API_URL}/campaigns')
    if response.status_code == 200:
        campaigns = response.json()
    else:
        campaigns = []
        flash('Failed to retrieve campaigns', 'danger')
    
    return render_template('sponsor/campaigns.html', campaigns=campaigns, title='Campaigns', form=form)


@sponsor.route('/campaigns/create', methods=['GET', 'POST'])
@login_required
def create_campaign():
    form = CampaignForm()
    if form.validate_on_submit():
        data = {
            'name': form.name.data,
            'description': form.description.data,
            'start_date': form.start_date.data.isoformat(),
            'end_date': form.end_date.data.isoformat(),
            'budget': form.budget.data,
            'visibility': form.visibility.data,
            'goals': form.goals.data,
            'sponsor_id': current_user.id
        }
        response = requests.post(f'{API_URL}/campaigns', json=data)
        if response.status_code == 201:
            flash('Campaign created successfully', 'success')
            return redirect(url_for('sponsor.manage_campaigns'))
        else:
            flash('Failed to create campaign', 'danger')
    
    return render_template('sponsor/create_campaign.html', title='Create Campaign', form=form)


@sponsor.route('/campaigns/<int:campaign_id>/edit', methods=['GET', 'POST', 'PUT'])
@login_required
def edit_campaign(campaign_id):

    campaign_ins = Campaign.query.get_or_404(campaign_id)
    form = CampaignForm(obj=campaign_ins)
    response = requests.get(f'{API_URL}/campaign/{campaign_id}')
    if response.status_code == 200:
        campaign = response.json()
    else:
        flash('Failed to retrieve campaign details', 'danger')
        return redirect(url_for('sponsor.manage_campaigns'))


    if form.validate_on_submit():
        data = {
            'name': form.name.data,
            'description': form.description.data,
            'start_date': form.start_date.data.isoformat(),
            'end_date': form.end_date.data.isoformat(),
            'budget': form.budget.data,
            'visibility': form.visibility.data,
            'goals': form.goals.data,
            'sponsor_id': current_user.id
        }
        response = requests.put(f'{API_URL}/campaign/{campaign_id}', json=data)
        print(f"Type of campaign_ins: {type(campaign_ins)}")
        print(f"Type of form: {type(form)}")

        if response.status_code == 200:
            flash('Campaign updated successfully', 'success')
            form.populate_obj(campaign_ins)
            return redirect(url_for('sponsor.manage_campaigns'))
        else:
            flash('Failed to update campaign', 'danger')
    
    return render_template('sponsor/edit_campaign.html', title='Edit Campaign', form=form, campaign=campaign)



@sponsor.route('/campaigns/<int:campaign_id>/delete', methods=['POST'])
@login_required
def delete_campaign(campaign_id):
    print(f"Delete request received for campaign ID: {campaign_id}")
    print(f"Request form data: {request.form}")

    if request.form.get('_method') == 'DELETE':
        response = requests.delete(f'{API_URL}/campaign/{campaign_id}')
        if response.status_code == 200:
            flash('Campaign deleted successfully', 'success')
        else:
            print(f"Error from API: {response.status_code} - {response.text}")
            flash('Failed to delete campaign', 'danger')
    else:
        flash('Invalid request method', 'danger')
    
    return redirect(url_for('sponsor.manage_campaigns'))




# Ad-request routes

# -----------------

# @sponsor.route('/campaign/<int:campaign_id>/ad_requests', methods=['GET', 'POST'])
# @login_required
# def ad_requests(campaign_id):
#     campaign = Campaign.query.get_or_404(campaign_id)
#     ad_requests = AdRequest.query.filter_by(campaign_id=campaign.id).all()
#     form = AdRequestForm()
#     if form.validate_on_submit():
#         ad_request = AdRequest(
#             campaign_id=campaign.id,
#             influencer_id=form.influencer_id.data,
#             status=form.status.data,
#             offer_amount=form.offer_amount.data
#         )
#         db.session.add(ad_request)
#         db.session.commit()
#         flash('Ad Request created!', 'success')
#         return redirect(url_for('sponsor.ad_requests', campaign_id=campaign.id))
#     return render_template('sponsor/manage_requests.html', ad_requests=ad_requests, form=form, campaign=campaign)