from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from maven.auth.forms import RegistrationForm, SponsorForm, InfluencerForm, LoginForm
from maven import db, bcrypt, login_manager
from maven.models import User, Sponsor, Influencer
from maven.auth.utils import save_picture, send_reset_email

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, role=form.role.data)
        user.set_password(form.password.data)
        user.check_password(form.confirm_password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please complete your profile.', 'success')
        if user.role == 'sponsor':
            return redirect(url_for('auth.signup_sponsor', user_id=user.id, title='Profile'))
        else:
            return redirect(url_for('auth.signup_influencer', user_id=user.id, title='Profile'))
    return render_template('auth/signup.html', form=form, title='Sign Up')


@auth.route('/signup/sponsor/<int:user_id>', methods=['GET', 'POST'])
def signup_sponsor(user_id):
    form = SponsorForm()
    if form.validate_on_submit():
        sponsor = Sponsor(user_id=user_id, company_name=form.company_name.data, industry=form.industry.data, budget=form.budget.data)
        db.session.add(sponsor)
        db.session.commit()
        flash('Sponsor profile created!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('sponsor/profile.html', form=form, title='Profile')


@auth.route('/signup/influencer/<int:user_id>', methods=['GET', 'POST'])
def signup_influencer(user_id):
    form = InfluencerForm()
    if form.validate_on_submit():
        influencer = Influencer(user_id=user_id, category=form.category.data, niche=form.niche.data, reach=form.reach.data)
        db.session.add(influencer)
        db.session.commit()
        flash('Influencer profile created!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('influencer/profile.html', form=form, title='Profile')


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
        else:
            return redirect(url_for('influencer.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            elif user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'sponsor':
                return redirect(url_for('sponsor.dashboard'))
            else:
                return redirect(url_for('influencer.dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('auth/login.html', form=form, title='Log In')


@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route("/forgotpassword")
def forgot_password():
    return redirect(url_for('auth.forgotten-password'))
