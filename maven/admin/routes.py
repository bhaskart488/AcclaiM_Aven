from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from maven import db
from maven.models import User, Campaign, AdRequest, Sponsor, Influencer


admin = Blueprint('admin', __name__)

@admin.before_app_request
def create_admin():
    if not User.query.filter_by(role='admin').first():
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('admin_password')
        db.session.add(admin)
        db.session.commit()



@admin.route("/admin-dashboard")
@login_required
def dashboard():
    active_users = User.query.filter_by(is_active=True).count()
    total_campaigns = Campaign.query.count()
    public_campaigns = Campaign.query.filter_by(visibility='public').count()
    private_campaigns = Campaign.query.filter_by(visibility='private').count()
    ad_requests = AdRequest.query.count()
    # flagged_sponsors = Sponsor.query.filter_by(is_flagged=True).count()
    flagged_sponsors = Sponsor.query.count()

    # flagged_influencers = Influencer.query.filter_by(is_flagged=True).count()
    flagged_influencers = Influencer.query.count()


    return render_template(
        'admin/dashboard.html',
        active_users=active_users,
        total_campaigns=total_campaigns,
        public_campaigns=public_campaigns,
        private_campaigns=private_campaigns,
        ad_requests=ad_requests,
        flagged_sponsors=flagged_sponsors,
        flagged_influencers=flagged_influencers
    )