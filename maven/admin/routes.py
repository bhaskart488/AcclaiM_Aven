from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from maven import db
from maven.models import User, Sponsor, Influencer

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
    return render_template('admin/dashboard.html', title='Admin')
