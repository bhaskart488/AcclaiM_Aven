from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from maven import db, bcrypt
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'sponsor', 'influencer'

    influencer = db.relationship('Influencer', uselist=False, backref='user', lazy=True)
    sponsor = db.relationship('Sponsor', uselist=False, backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    address = db.Column(db.String(200))
    category = db.Column(db.String(50))
    niche = db.Column(db.String(200))
    profile_picture = db.Column(db.String(100), default='default.jpg')

    def __repr__(self):
        return f'<Influencer {self.full_name}>'


class Sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    budget = db.Column(db.String(50))
    address = db.Column(db.String(200))
    category = db.Column(db.String(50))
    profile_picture = db.Column(db.String(100), default='default.jpg')

    def __repr__(self):
        return f'<Sponsor {self.full_name}>'





class Campaign(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    budget = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

class Ad(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    platform = db.Column(db.String(80), nullable=False)

