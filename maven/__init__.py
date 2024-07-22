import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_restful import Api
from maven.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from maven.main.routes import main
    from maven.auth.routes import auth
    from maven.errors.handlers import errors
    from maven.admin.routes import admin
    from maven.influencer.routes import influencer
    from maven.sponsor.routes import sponsor

    from maven.api import api_bp

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(errors)
    app.register_blueprint(admin)
    app.register_blueprint(influencer)
    app.register_blueprint(sponsor)
    app.register_blueprint(api_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()  # Create tables for our models

    return app

