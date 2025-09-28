from dotenv import load_dotenv
import os
from datetime import timedelta
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PROPAGATE_EXCEPTIONS = True
    CORS_HEADERS = 'Content-Type'
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwtsecretkey")  
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=3600)
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

    
