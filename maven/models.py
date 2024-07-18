from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from maven import db, bcrypt
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'sponsor', 'influencer'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_name = db.Column(db.String(120))
    industry = db.Column(db.String(120))
    budget = db.Column(db.Float)

class Influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(120))
    niche = db.Column(db.String(120))
    reach = db.Column(db.Integer)



# def init_db():
#     db.create_all()
