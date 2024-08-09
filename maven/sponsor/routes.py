import os
from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import login_user, current_user, logout_user, login_required
from maven import db
from maven.models import User, Sponsor, Campaign, AdRequest, Influencer
from maven.sponsor.forms import SponsorForm, CampaignForm, AdRequestForm, InfluencerSearchForm
from werkzeug.utils import secure_filename
import requests

sponsor = Blueprint('sponsor', __name__)

# def get_current_sponsor():
#     return Sponsor.query.filter_by(user_id=current_user.id).first()

def check_campaign_ownership(campaign_id):
    # Retrieve the campaign
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Check if the current user is the sponsor of the campaign
    if campaign.sponsor_id == current_user.id:
        return True
    else:
        return False


def check_ad_request_ownership(ad_request_id):
    # Retrieve the ad request
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    
    # Access the campaign associated with the ad request
    # campaign = Campaign.query.get_or_404(ad_request.campaign_id)
    
    return check_campaign_ownership(ad_request.campaign_id)
    

# Sponsor dashboard

@sponsor.route('/sponsor-dashboard')
@login_required
def dashboard():
    return render_template('sponsor/dashboard.html', title='Sponsor')


# Sponsor Profile delete 

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



# Sponsor Profile Create and Update

@sponsor.route('/sponsor/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    if request.method == 'POST':
        print("Profile route received a POST request")

    if request.method == 'GET':
        print("Profile route received a GET request")
    
    form = SponsorForm()

    print(f"Received user_id: {user_id}")

    try:
        sponsor = Sponsor.query.filter_by(user_id=user_id).first_or_404()
        print(f"Sponsor found: {sponsor}")
    except Exception as e:
        print(f"Error retrieving sponsor: {e}")
        return render_template('errors/404.html'), 404
    
    # Check if the current user is the owner of the profile
    is_owner = sponsor.user_id == current_user.id
    print(f"Is owner: {is_owner}")

    if not is_owner:
        # Pre-fill the form fields with sponsor data
        # Load existing sponsor details
        form.full_name.data = sponsor.full_name
        form.email.data = sponsor.email
        form.phone.data = sponsor.phone
        form.mobile.data = sponsor.mobile
        form.address.data = sponsor.address
        form.industry.data = sponsor.industry
        form.website.data = sponsor.website
        form.budget.data = sponsor.budget

        

    if form.validate_on_submit():
        print("Profile route received validate request")
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

    # return render_template('sponsor/profile.html', title='Profile', form=form, sponsor=sponsor)
    # Render the profile template with different context based on whether the current user is the owner
    if is_owner:
        return render_template('sponsor/profile.html', title='Profile', form=form, sponsor=sponsor)
    else:
        return render_template('sponsor/profile_visitor.html', title='Profile', sponsor=sponsor)


API_URL = 'http://localhost:5000/api'  # Replace with the actual API URL


# ------------------------

# Campaign Management Route

# -------------------------

@sponsor.route('/campaigns/', methods=['GET', 'POST'])
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
    
    # response = requests.get(f'{API_URL}/campaigns')
    # if response.status_code == 200:
    #     campaigns = response.json()
    # else:
    #     campaigns = []
    #     flash('Failed to retrieve campaigns', 'danger')
    
    # Retrieve campaigns associated with the current sponsor
    
    campaigns = Campaign.query.filter(Campaign.sponsor_id == current_user.id).all()
    

    return render_template('sponsor/campaigns.html', campaigns=campaigns, title='Campaigns', form=form)


# Campaign Create Route

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


# Campaign Edit Route

@sponsor.route('/campaigns/<int:campaign_id>/edit', methods=['GET', 'POST', 'PUT'])
@login_required
def edit_campaign(campaign_id):
    if not check_campaign_ownership(campaign_id):
        abort(403)  # Forbidden

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


# Campaign Delete Route

@sponsor.route('/campaigns/<int:campaign_id>/delete', methods=['POST'])
@login_required
def delete_campaign(campaign_id):
    if not check_campaign_ownership(campaign_id):
        abort(403)  # Forbidden
        
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


# ---------------------------

# Ad Request Management Route

# ---------------------------


@sponsor.route('/ad_requests/<int:campaign_id>', methods=['GET', 'POST'])
@login_required
def manage_ad_requests(campaign_id):
    form = AdRequestForm()
    sponsor_id = current_user.id
    print('campaign_id:', campaign_id, 'sponsor_id:', sponsor_id)

    if request.method == 'POST':
        data = {
            'campaign_id': campaign_id,
            'influencer_id': request.form.get('influencer_id'),
            'messages': request.form.get('messages'),
            'requirements': request.form.get('requirements'),
            'status': request.form.get('status'),
            'offer_amount': request.form.get('offer_amount'),
        }
        response = requests.post(f'{API_URL}/ad_requests', json=data)
        if response.status_code == 201:
            flash('Ad Request created successfully', 'success')
        else:
            flash('Failed to create Ad Request', 'danger')
        return redirect(url_for('sponsor.manage_ad_requests', campaign_id=campaign_id))
    
    response = requests.get(f'{API_URL}/ad_requests?campaign_id={campaign_id}&sponsor_id={sponsor_id}')
    if response.status_code == 200:
        ad_requests = response.json()
    else:
        ad_requests = []
        flash('Failed to retrieve ad requests', 'danger')

    ad_requests = AdRequest.query.join(Campaign).filter(Campaign.sponsor_id == current_user.id, Campaign.id == campaign_id).all()
    print(ad_requests)
    
    return render_template('sponsor/ad_requests.html', ad_requests=ad_requests, title='Ad Requests', form=form, campaign_id=campaign_id)

# Ad Request Create Route

@sponsor.route('/campaigns/<int:campaign_id>/ad_requests/create', methods=['GET', 'POST'])
@login_required
def create_ad_request(campaign_id):
    form = AdRequestForm()
    sponsor_id = current_user.id
    # campaign_id = request.form.get('campaign_id')

    if form.validate_on_submit():
        data = {
            'campaign_id': campaign_id,
            'influencer_id': form.influencer_id.data,
            'messages': form.messages.data,
            'requirements': form.requirements.data,
            'status': form.status.data,
            'offer_amount': float(form.offer_amount.data),
            'sponsor_id': sponsor_id
        }
        response = requests.post(f'{API_URL}/ad_requests', json=data)
        if response.status_code == 201:
            flash('Ad Request created successfully', 'success')
            return redirect(url_for('sponsor.manage_ad_requests', campaign_id=campaign_id))
        else:
            flash('Failed to create Ad Request', 'danger')
    
    # print(campaign_id)


    influencers = Influencer.query.all()
    print(influencers)
    return render_template('sponsor/create_ad_request.html', title='Create Ad Request', form=form, campaign_id=campaign_id, influencers=influencers)


# Ad Request Edit Route

@sponsor.route('/ad_requests/<int:ad_request_id>/edit', methods=['GET', 'POST', 'PUT'])
@login_required
def edit_ad_request(ad_request_id):
    if not check_ad_request_ownership(ad_request_id):
        abort(403)  # Forbidden

    ad_request_ins = AdRequest.query.get_or_404(ad_request_id)
    form = AdRequestForm(obj=ad_request_ins)
    response = requests.get(f'{API_URL}/ad_request/{ad_request_id}')
    if response.status_code == 200:
        ad_request = response.json()
    else:
        flash('Failed to retrieve Ad request details', 'danger')
        return redirect(url_for('sponsor.manage_ad_requests', campaign_id=ad_request['campaign_id']))

    if form.validate_on_submit():
        data = {
            'campaign_id': form.campaign_id.data,
            'influencer_id': form.influencer_id.data,
            'messages': form.messages.data,
            'requirements': form.requirements.data,
            'status': form.status.data,
            'offer_amount': float(form.offer_amount.data),
        }
        response = requests.put(f'{API_URL}/ad_request/{ad_request_id}', json=data)
        print(f"Type of ad_request_ins: {type(ad_request_ins)}")
        print(f"Type of form: {type(form)}")

        if response.status_code == 200:
            flash('Ad Request updated successfully', 'success')
            form.populate_obj(ad_request_ins)
            return redirect(url_for('sponsor.manage_ad_requests', campaign_id=ad_request['campaign_id']))
        else:
            flash('Failed to update Ad Request', 'danger')
    
    return render_template('sponsor/edit_ad_request.html', title='Edit Ad Request', form=form, ad_request=ad_request)

# Ad Request Delete Route

@sponsor.route('/ad_requests/<int:ad_request_id>/delete', methods=['POST'])
@login_required
def delete_ad_request(ad_request_id):
    if not check_ad_request_ownership(ad_request_id):
        abort(403)  # Forbidden

    print(f"Delete request received for Ad request ID: {ad_request_id}")
    print(f"Request form data: {request.form}")
    
    if request.form.get('_method') == 'DELETE':
        response = requests.delete(f'{API_URL}/ad_request/{ad_request_id}')
        if response.status_code == 200:
            flash('Ad Request deleted successfully', 'success')
        else:
            print(f"Error from API: {response.status_code} - {response.text}")
            flash('Failed to delete Ad Request', 'danger')
    else:
        flash('Invalid request method', 'danger')
    # ad_request = AdRequest.query.get_or_404(ad_request_id)
    return redirect(url_for('sponsor.manage_campaigns'))


# ----------------------

# search routes

# ----------------------



@sponsor.route('/search_influencers', methods=['GET', 'POST'])
@login_required
def search_influencers():
    form = InfluencerSearchForm()
    influencers = []
    if form.validate_on_submit():
        niche = form.niche.data
        influencers = Influencer.query.filter_by(niche=niche).all()
    return render_template('sponsor/search_results.html', form=form, influencers=influencers)