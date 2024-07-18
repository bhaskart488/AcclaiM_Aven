from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from maven import db, bcrypt, login_manager
from maven.models import User, Sponsor, Influencer

admin = Blueprint('admin', __name__)


@admin.before_app_request
def create_admin():
    if not User.query.filter_by(role='admin').first():
        admin = User(username='admin', email='admin@gmail.com', role='admin')
        admin.set_password("thesuperadmin")
        admin.set_password('admin_password')
        db.session.add(admin)
        db.session.commit()

@admin.route("/admin-dashboard")
def dashboard():
    return redirect(url_for('admin.dashboard', title='Admin'))