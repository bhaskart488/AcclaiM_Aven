import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('secret')
    SQLALCHEMY_DATABASE_URI = os.getenv('uri')

