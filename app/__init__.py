from flask import Flask, jsonify
from flask_cors import CORS
from app.extends import db
from flask_migrate import Migrate
from config import Config
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
import os
from .routes import init_routes

migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app, supports_credentials=True)
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    init_routes(app)
    with app.app_context():
        from app.models import user,rekomendasi
       

    return app
