from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
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
    twitter_handle = db.Column(db.String(50))
    twitter_followers = db.Column(db.Integer)
    instagram_handle = db.Column(db.String(50))
    instagram_followers = db.Column(db.Integer)
    facebook_handle = db.Column(db.String(50))
    facebook_followers = db.Column(db.Integer)

    def __repr__(self):
        return f'<Influencer {self.full_name}>'


class Sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    address = db.Column(db.String(200))
    industry = db.Column(db.String(50))
    profile_picture = db.Column(db.String(100), default='default.jpg')
    website = db.Column(db.String(50))
    budget = db.Column(db.Integer)
    
    def __repr__(self):
        return f'<Sponsor {self.full_name}>'


class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    visibility = db.Column(db.String(10), nullable=False)  # 'public' or 'private'
    goals = db.Column(db.String(200))
    
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    sponsor = db.relationship('Sponsor', backref=db.backref('campaigns', lazy=True))
    
    ad_requests = db.relationship('AdRequest', backref='campaign', lazy=True)
    
    def __repr__(self):
        return f'<Campaign {self.name}>'


class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    messages = db.Column(db.Text)
    requirements = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='Pending')  # 'Pending', 'Accepted', 'Rejected'
    offer_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"AdRequest('{self.campaign_id}', '{self.influencer_id}', '{self.status}')"


class CampaignSchema(SQLAlchemyAutoSchema):
    start_date = fields.DateTime(format='%Y-%m-%d')  # Ensure proper format
    end_date = fields.DateTime(format='%Y-%m-%d')    # Ensure proper format

    class Meta:
        model = Campaign
        include_relationships = True
        load_instance = True

campaign_schema = CampaignSchema()
campaigns_schema = CampaignSchema(many=True)


class AdRequestSchema(SQLAlchemyAutoSchema):
    created_at = fields.DateTime(format='%Y-%m-%d')  # Ensure proper format
    updated_at = fields.DateTime(format='%Y-%m-%d')    # Ensure proper format

    class Meta:
        model = AdRequest
        include_relationships = True
        load_instance = True

adRequest_schema = AdRequestSchema()
adRequests_schema = AdRequestSchema(many=True)

    
