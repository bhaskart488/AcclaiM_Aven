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
    

    return render_template(
        'admin/dashboard.html',
        active_users=active_users,
        total_users=total_users,
        total_sponsors=total_sponsors,
        total_influencers=total_infleuncers,
        total_campaigns=total_campaigns,
        public_campaigns=public_campaigns,
        private_campaigns=private_campaigns,
        ad_requests=ad_requests,
        flagged_users=flagged_users,
        flagged_campaigns=flagged_campaigns,
        title = 'Admin'
    )


@admin.route("/admin/delete_user/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.role == 'sponsor':
        sponsor = Sponsor.query.filter_by(user_id=user.id).first()
        db.session.delete(sponsor)

        campaigns = Campaign.query.filter_by(sponsor_id=user.id).all()
        for campaign in campaigns:
            # Handle related records in the ad_request table
            ad_requests = AdRequest.query.filter_by(campaign_id=campaign.id).all()
            for ad_request in ad_requests:
                db.session.delete(ad_request)  
            db.session.delete(campaign)
    

    if user.role == 'influencer':
        influencer = Influencer.query.filter_by(user_id=user.id).first()
        db.session.delete(influencer)

    db.session.delete(user)
    db.session.commit()
    flash('User has been deleted.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin.route("/admin/delete_campaign/<int:campaign_id>", methods=["POST"])
@login_required
def delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    # Handle related records in the ad_request table
    ad_requests = AdRequest.query.filter_by(campaign_id=campaign.id).all()
    for ad_request in ad_requests:
        db.session.delete(ad_request)  
    
    db.session.delete(campaign)
    db.session.commit()
    flash('Campaign has been deleted.', 'success')
    return redirect(url_for('admin.dashboard'))



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


@admin.route('/search_campaigns', methods=['GET', 'POST'])
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
        visibility = form.visibility.data

        query = Campaign.query.join(Sponsor, Sponsor.user_id == Campaign.sponsor_id)
        if visibility:
            query = query.filter(Campaign.visibility == visibility)
        if industry:
            query = query.filter(Sponsor.industry == industry)
        if budget:
            query = query.filter(Campaign.budget <= budget)
        if sponsor_name:
            query = query.filter(Sponsor.full_name.ilike(f'%{sponsor_name}%'))
        campaigns = query.add_columns(Sponsor.full_name, Sponsor.website).all()

    return render_template('admin/search_campaigns.html', form=form, campaigns=campaigns, industry=industry, budget=budget, sponsor_name=sponsor_name, title='Campaigns')



@admin.route('/search_users', methods=['GET', 'POST'])
@login_required
def search_users():
    form = UserSearchForm()
    users = []
    if form.validate_on_submit():
        industry = form.industry.data
        category = form.category.data
        user_type = form.user_type.data

        query = User.query
        if user_type:
            if user_type == 'sponsor':
                if industry:
                    query = query.join(Sponsor).filter(Sponsor.industry == industry)
                else:
                    query = query.filter(User.role == 'sponsor')
            elif user_type == 'influencer':
                if category:
                    query = query.join(Influencer).filter(Influencer.category == category)
                else:
                    query = query.filter(User.role == 'influencer')
        if industry and not category:
            query = query.join(Sponsor).filter(Sponsor.industry == industry)
        if category and not industry:
            query = query.join(Influencer).filter(Influencer.category == category)
        if not user_type and not industry and not category:
            query = query.filter(User.role != 'admin')

        users = query.all()

    return render_template('admin/search_users.html', form=form, users=users, title='Users')


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

    return render_template('admin/analytics.html', data=data, title='Analytics')