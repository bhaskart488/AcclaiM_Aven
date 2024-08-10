import os
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
import requests
from maven.auth.forms import RegistrationForm, LoginForm
from maven import db, bcrypt, login_manager
from maven.models import User, Sponsor, Influencer, Notification
from werkzeug.utils import secure_filename

auth = Blueprint('auth', __name__)

API_URL = 'http://localhost:5000/api'  # Update this URL based on your app's running address

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        data = {
            'username': form.username.data,
            'email': form.email.data,
            'password': form.password.data,
            'role': form.role.data
        }
        response = requests.post(f'{API_URL}/register', json=data)
        
        if response.status_code == 201:

            response_data = response.json()
            user_data = {
                'id': response_data['id'],
                'username': response_data['username'],
                'email': response_data['email'],
                'role': response_data['role']
            }
            user = User(**user_data)
            print(response_data)


            # Create profile based on role
            if user.role == 'sponsor':
                sponsor = Sponsor(user_id=user_data['id'], email=user_data['email'], full_name=user_data['username'])
                db.session.add(sponsor)
            elif user.role == 'influencer':
                influencer = Influencer(user_id=user_data['id'], email=user_data['email'], full_name=user_data['username'])
                db.session.add(influencer)


            # Send notification to admin
            admin_id = 1
            notification = Notification(
                user_id = admin_id,
                message = f' {user_data['role']} {user_data['username']} is created.'
            )
            db.session.add(notification)

            db.session.commit()

            # Log in the user
            login_user(user)

            flash('Account created! Please complete your profile.', 'success')
            if user.role == 'sponsor':
                return redirect(url_for('sponsor.profile', user_id=user_data['id']))
            elif user.role == 'influencer':
                return redirect(url_for('influencer.profile', user_id=user_data['id']))
        else:
            flash(response.json().get('message', 'An error occurred'), 'danger')
    return render_template('auth/signup.html', form=form, title='Sign Up')



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'sponsor':
            return redirect(url_for('sponsor.dashboard'))
        elif current_user.role == 'influencer':
            return redirect(url_for('influencer.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        data = {
            'email': form.email.data,
            'password': form.password.data
        }
        response = requests.post(f'{API_URL}/login', json=data)
        
        if response.status_code == 200:
            response_data = response.json()
            user_data = {
                'id': response_data['id'],
                'username': response_data['username'],
                'email': response_data['email'],
                'role': response_data['role']
            }
            user = User(**user_data)
            login_user(user, remember=form.remember.data)
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            elif user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'sponsor':
                return redirect(url_for('sponsor.dashboard'))
            elif user.role == 'influencer':
                return redirect(url_for('influencer.dashboard'))
        else:
            flash(response.json().get('message', 'An error occurred'), 'danger')
    return render_template('auth/login.html', form=form, title='Log In')


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route("/forgotpassword")
def forgot_password():
    return redirect(url_for('auth.forgotten_password'))


