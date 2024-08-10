from flask import abort, render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from maven.admin.forms import UserSearchForm, CampaignSearchForm
from maven import db
from maven.models import User, Campaign, AdRequest, Sponsor, Influencer
import os


admin = Blueprint('admin', __name__)


@admin.before_app_request
def create_admin():
    if not User.query.filter_by(role='admin').first():
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password(os.getenv('ADMIN_PASSWORD'))
        db.session.add(admin)
        db.session.commit()


@admin.route("/admin-dashboard")
@login_required
def dashboard():
    active_users = User.query.filter_by(is_active=True).count()
    total_users = User.query.count()
    total_sponsors = User.query.filter_by(role='sponsor').count()
    total_infleuncers = User.query.filter_by(role='influencer').count()
    total_campaigns = Campaign.query.count()
    public_campaigns = Campaign.query.filter_by(visibility='public').count()
    private_campaigns = Campaign.query.filter_by(visibility='private').count()
    ad_requests = AdRequest.query.count()
    flagged_users = User.query.filter_by(flagged=True).all()
    flagged_campaigns = Campaign.query.filter_by(flagged=True).all()
    # flagged_sponsors = Sponsor.query.filter_by(is_flagged=True).count()
    # flagged_influencers = Influencer.query.filter_by(is_flagged=True).count()
    # flagged_sponsors = User.query.filter_by(flagged=True, role='sponsor').count()
    # flagged_influencers = User.query.filter_by(flagged=True, role='influencer').count()
    

    return render_template(
        'admin/dashboard.html',
        active_users=active_users,
        total_users=total_users,
        total_sponsors=total_sponsors,
        total_influencers=total_infleuncers,
        total_campaigns=total_campaigns,
        public_campaigns=public_campaigns,
        private_campaigns=private_campaigns,
        # flagged_sponsors=flagged_sponsors,
        # flagged_influencers=flagged_influencers
        ad_requests=ad_requests,
        flagged_users=flagged_users,
        flagged_campaigns=flagged_campaigns,
        title = 'Admin'
    )



@admin.route('/flag_user/<int:user_id>', methods=['POST', 'GET'])
@login_required
def flag_user(user_id):
    user = User.query.get_or_404(user_id)
    user.flagged = True
    db.session.commit()
    flash('User has been flagged.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin.route('/unflag_user/<int:user_id>', methods=['POST', 'GET'])
@login_required
def unflag_user(user_id):
    user = User.query.get_or_404(user_id)
    user.flagged = False
    db.session.commit()
    flash('User has been unflagged.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin.route('/flag_campaign/<int:campaign_id>', methods=['POST', 'GET'])
@login_required
def flag_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    campaign.flagged = True
    db.session.commit()
    flash('Campaign has been flagged.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin.route('/unflag_campaign/<int:campaign_id>', methods=['POST', 'GET'])
@login_required
def unflag_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    campaign.flagged = False
    db.session.commit()
    flash('Campaign has been unflagged.', 'success')
    return redirect(url_for('admin.dashboard'))


# search routes

# @admin.route('/search_campaigns', methods=['GET', 'POST'])
# @login_required
# def search_campaigns():
#     campaigns = Campaign.query.all()
#     return render_template('admin/search_campaigns.html', campaigns=campaigns, title='Admin/Campaigns')


@admin.route('/search_campaigns', methods=['GET', 'POST'])
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
        visibility = form.visibility.data

        query = Campaign.query.join(Sponsor, Sponsor.user_id == Campaign.sponsor_id).filter(
            Campaign.visibility == 'public'
        )
        if visibility:
            query = query.filter(Campaign.visibility == visibility)
        if industry:
            query = query.filter(Sponsor.industry == industry)
        if budget:
            query = query.filter(Campaign.budget <= budget)
        if sponsor_name:
            query = query.filter(Sponsor.full_name.ilike(f'%{sponsor_name}%'))
        campaigns = query.add_columns(Sponsor.full_name, Sponsor.website).all()

    return render_template('admin/search_campaigns.html', form=form, campaigns=campaigns, industry=industry, budget=budget, sponsor_name=sponsor_name)

    

# @admin.route('/search_users', methods=['GET', 'POST'])
# @login_required
# def search_users():
#     users = User.query.all()
#     return render_template('admin/search_users.html', users=users)


@admin.route('/search_users', methods=['GET', 'POST'])
def search_users():
    form = UserSearchForm()
    users = []
    if form.validate_on_submit():
        industry = form.industry.data
        niche = form.niche.data
        user_type = form.user_type.data

        query = User.query
        if user_type == 'sponsor':
            query = query.join(Sponsor).filter(Sponsor.industry == industry)
        elif user_type == 'influencer':
            query = query.join(Influencer).filter(Influencer.niche == niche)

        users = query.all()

    return render_template('admin/search_users.html', form=form, users=users)


# view_details

@admin.route('/campaign/<int:campaign_id>', methods=['GET'])
@login_required
def view_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    completed_ad_requests = AdRequest.query.filter_by(campaign_id=campaign_id, status='completed').count()
    pending_ad_requests = AdRequest.query.filter_by(campaign_id=campaign_id, status='pending').count()
    rejected_ad_requests = AdRequest.query.filter_by(campaign_id=campaign_id, status='rejected').count()
    total_ad_requests = AdRequest.query.filter_by(campaign_id=campaign_id).count()
    if total_ad_requests > 0:
        progress = float(completed_ad_requests / total_ad_requests)
    else:
        progress = float(0)
    
    
    print('debug statement', completed_ad_requests, pending_ad_requests, rejected_ad_requests, total_ad_requests)
    return render_template('admin/view_campaign.html',
                            campaign=campaign, 
                            progress=progress,
                            pending_ad_requests=pending_ad_requests,
                            completed_ad_requests=completed_ad_requests,
                            rejected_ad_requests=rejected_ad_requests,
                            title = 'Progress'
                    )


@admin.route('/user/<int:user_id>', methods=['GET'])
@login_required
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'sponsor':
        return redirect(url_for('sponsor.profile', user_id=user.id))
    elif user.role == 'influencer':
        return redirect(url_for('influencer.profile', user_id=user.id))
    else:
        abort(404)


#analytics


@admin.route('/admin/analytics')
@login_required
def admin_analytics():
    # Query for ad request statuses
    ad_request_statuses = db.session.query(
        AdRequest.status, db.func.count(AdRequest.id)
    ).group_by(AdRequest.status).all()

    # Query for ad request completion statuses
    ad_request_completion_statuses = db.session.query(
        AdRequest.completion_status, db.func.count(AdRequest.id)
    ).group_by(AdRequest.completion_status).all()

    # Query for offer amount sum per campaign
    offer_amounts = db.session.query(
        Campaign.name, db.func.sum(AdRequest.offer_amount)
    ).join(AdRequest).group_by(Campaign.name).all()

    # Query for campaign progress
    campaigns = Campaign.query.all()
    campaign_progress = [(campaign.name, campaign.campaign_progress()*100) for campaign in campaigns]

    # Query for campaign start and end dates
    campaign_dates = db.session.query(
        Campaign.name, Campaign.start_date, Campaign.end_date
    ).all()

    # Query for total budget of all sponsors
    total_sponsor_budget = db.session.query(db.func.sum(Sponsor.budget)).scalar()

    # Query for number of public and private campaigns
    public_campaigns_count = Campaign.query.filter_by(visibility='public').count()
    private_campaigns_count = Campaign.query.filter_by(visibility='private').count()

    # Query for budget of each campaign
    campaign_budgets = db.session.query(
        Campaign.name, Campaign.budget
    ).all()

    # Query for total earnings of all influencers
    total_earnings = db.session.query(db.func.sum(AdRequest.offer_amount)).scalar()

    data = {
        'ad_request_statuses': list(ad_request_statuses),
        'ad_request_completion_statuses': list(ad_request_completion_statuses),
        'offer_amounts': list(offer_amounts),
        'campaign_progress': list(campaign_progress),
        'campaign_dates': list(campaign_dates),
        'total_sponsor_budget': total_sponsor_budget,
        'public_campaigns_count': public_campaigns_count,
        'private_campaigns_count': private_campaigns_count,
        'campaign_budgets': list(campaign_budgets),
        'total_earnings': total_earnings,
        'campaign_visibility': {
            'public': public_campaigns_count,
            'private': private_campaigns_count
        }
    }

    return render_template('admin/analytics.html', data=data)