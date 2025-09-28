from flask import request, jsonify
from app.models import user, rekomendasi
from flask import Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

root = Blueprint('root', __name__)


@root.get("/")
def index():
    return "Hello World!"