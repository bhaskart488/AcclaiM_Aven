from flask import render_template, request, Blueprint, url_for
from maven.models import Notification
from flask_login import login_required, current_user

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def index():    
    return render_template('main/index.html', title='Welcome')

@main.route("/pricing")
def pricing():    
    return render_template('main/pricing.html', title='Pricing')

@main.route("/contacts")
def contacts():    
    return render_template('main/contacts.html', title='Contact Us')

@main.route("/notifications")
@login_required
def notifications():    
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.timestamp.desc()).all()
    return render_template('main/notifications.html', notifications=notifications, title='Notifications')
    # return render_template('main/notifications.html', title='Contacts')

