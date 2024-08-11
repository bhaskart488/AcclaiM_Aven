from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from maven import db, bcrypt
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash



class User(db.Model, UserMixin):
    """
    Represents a user in the system.
    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        password_hash (str): The hashed password of the user.
        email (str): The email address of the user.
        role (str): The role of the user. Possible values are 'admin', 'sponsor', 'influencer'.
        flagged (bool): Indicates if the user is flagged.
        influencer (Influencer): The associated influencer profile.
        sponsor (Sponsor): The associated sponsor profile.
    Methods:
        set_password(password): Sets the password for the user.
        check_password(password): Checks if the provided password matches the user's password.
        unread_notifications_count: Returns the count of unread notifications for the user.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'sponsor', 'influencer'
    flagged = db.Column(db.Boolean, default=False)  # New field

    influencer = db.relationship('Influencer', uselist=False, backref='user', lazy=True)
    sponsor = db.relationship('Sponsor', uselist=False, backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def unread_notifications_count(self):
        return Notification.query.filter_by(user_id=self.id, is_read=False).count()


class Influencer(db.Model):
    """
    Represents an influencer in the system.
    Attributes:
        id (int): The unique identifier of the influencer.
        user_id (int): The foreign key referencing the associated user.
        full_name (str): The full name of the influencer.
        email (str): The email address of the influencer.
        phone (str): The phone number of the influencer.
        mobile (str): The mobile number of the influencer.
        address (str): The address of the influencer.
        category (str): The category of the influencer.
        niche (str): The niche of the influencer.
        profile_picture (str): The filename of the influencer's profile picture.
        twitter_handle (str): The Twitter handle of the influencer.
        twitter_followers (int): The number of Twitter followers of the influencer.
        instagram_handle (str): The Instagram handle of the influencer.
        instagram_followers (int): The number of Instagram followers of the influencer.
        facebook_handle (str): The Facebook handle of the influencer.
        facebook_followers (int): The number of Facebook followers of the influencer.
    """

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
    """
    Represents a sponsor in the system.
    Attributes:
        id (int): The unique identifier of the sponsor.
        user_id (int): The foreign key referencing the associated user.
        full_name (str): The full name of the sponsor.
        email (str): The email address of the sponsor.
        phone (str): The phone number of the sponsor.
        mobile (str): The mobile number of the sponsor.
        address (str): The address of the sponsor.
        industry (str): The industry of the sponsor.
        profile_picture (str): The filename of the sponsor's profile picture.
        website (str): The website of the sponsor.
        budget (int): The budget of the sponsor.
    """
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
    """
    Represents a campaign in the system.
    Attributes:
        id (int): The unique identifier of the campaign.
        name (str): The name of the campaign.
        description (str): The description of the campaign.
        start_date (datetime.date): The start date of the campaign.
        end_date (datetime.date): The end date of the campaign.
        budget (int): The budget of the campaign.
        visibility (str): The visibility of the campaign. Possible values are 'public' or 'private'.
        goals (str): The goals of the campaign.
        flagged (bool): Indicates if the campaign is flagged.
        sponsor_id (int): The foreign key referencing the associated sponsor.
        sponsor (Sponsor): The associated sponsor.
        ad_requests (list[AdRequest]): The list of ad requests associated with the campaign.
    Methods:
        campaign_progress(): Returns the progress of the campaign.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    visibility = db.Column(db.String(10), nullable=False)  # 'public' or 'private'
    goals = db.Column(db.String(200))
    flagged = db.Column(db.Boolean, default=False)  # New field
    
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    sponsor = db.relationship('Sponsor', backref=db.backref('campaigns', lazy=True))
    
    ad_requests = db.relationship('AdRequest', backref='campaign', lazy=True)
    
    def __repr__(self):
        return f'<Campaign {self.name}>'
    
    def campaign_progress(self):
        total_ad_requests = len(self.ad_requests)
        if total_ad_requests == 0:
            return 0.0
        completed_ad_requests = len([ad_request for ad_request in self.ad_requests if ad_request.completion_status == 'Complete'])
        return completed_ad_requests / total_ad_requests


class AdRequest(db.Model):
    """
    Represents an ad request in the system.
    Attributes:
        id (int): The unique identifier of the ad request.
        campaign_id (int): The foreign key referencing the associated campaign.
        influencer_id (int): The foreign key referencing the associated influencer or user.
        messages (str): The messages related to the ad request.
        requirements (str): The requirements of the ad request.
        status (str): The status of the ad request. Possible values are 'Pending', 'Accepted', 'Rejected'.
        offer_amount (float): The offer amount of the ad request.
        created_at (datetime.datetime): The creation timestamp of the ad request.
        updated_at (datetime.datetime): The last update timestamp of the ad request.
        completion_status (str): The completion status of the ad request.
    Methods:
        __repr__(): Returns a string representation of the ad request.
    """

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    # if request created when logged in user is sponsor, influencer id will be selected from dropdown as the names of influencers
    # if request created when logged in user is influencer, influencer id will be set to logged in user
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    messages = db.Column(db.Text)
    requirements = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='Pending')  # 'Pending', 'Accepted', 'Rejected'
    offer_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # New column for completion status
    completion_status = db.Column(db.String(20), nullable=False, default='Incomplete')

    def __repr__(self):
        return f"AdRequest('{self.campaign_id}', '{self.influencer_id}', '{self.status}')"


class CampaignSchema(SQLAlchemyAutoSchema):
    start_date = fields.DateTime(format='%Y-%m-%d')  
    end_date = fields.DateTime(format='%Y-%m-%d')    

    class Meta:
        model = Campaign
        include_relationships = True
        load_instance = True

campaign_schema = CampaignSchema()
campaigns_schema = CampaignSchema(many=True)


class AdRequestSchema(SQLAlchemyAutoSchema):
    created_at = fields.DateTime(format='%Y-%m-%d')  
    updated_at = fields.DateTime(format='%Y-%m-%d')    

    class Meta:
        model = AdRequest
        include_relationships = True
        load_instance = True

adRequest_schema = AdRequestSchema()
adRequests_schema = AdRequestSchema(many=True)

    
class Notification(db.Model):
    """
    Represents a notification in the system.
    Attributes:
        id (int): The unique identifier of the notification.
        user_id (int): The foreign key referencing the associated user.
        message (str): The message of the notification.
        timestamp (datetime.datetime): The timestamp of the notification.
        is_read (bool): Indicates if the notification has been read.
    Methods:
        __repr__(): Returns a string representation of the notification.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f'<Notification {self.message}>'