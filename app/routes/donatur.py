from flask import request, jsonify, Blueprint
from datetime import timedelta, datetime
from sqlalchemy import or_
from app.models.user import Donatur
from app.extends import db, bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

donatur = Blueprint('donatur', __name__)


@donatur.post("/api/post/login")
def donatur_login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    try:
        donatur_user = Donatur.query.filter_by(email=email).first()
        if donatur_user and bcrypt.check_password_hash(donatur_user.password, password):
            access_token = create_access_token(
                identity=str(donatur_user.id),
                expires_delta=timedelta(hours=1)
            )
            donatur_user.login_stamp = datetime.now()
            db.session.commit()

            return jsonify({
                "access_token" : access_token,
            })

        return jsonify({"message": "Email atau password salah"}), 401
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@donatur.get('/api/get/username')
@jwt_required()
def get_username():
    current_user_id = get_jwt_identity()
    donatur_user = Donatur.query.get(int(current_user_id))

    if not donatur_user:
        return jsonify({"message": "Donatur tidak ditemukan"}), 404

    return jsonify({"user": donatur_user.username}), 200

@donatur.post("/api/post/daftar")
def donatur_daftar():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")

    try:
        existing_user = Donatur.query.filter(
            or_(Donatur.username == username, Donatur.email == email)
        ).first()
        if existing_user:
            return jsonify({"message": "Email atau Username sudah digunakan"}), 400

        new_user = Donatur(
            name=name,
            email=email,
            username=username,
            password=bcrypt.generate_password_hash(password).decode('utf-8'),
            login_stamp=None
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "Daftar berhasil"}), 201

    except Exception as e:
        return jsonify({"message": str(e)}), 500

@donatur.get('/api/get/data/account')
@jwt_required()
def get_donatur_akun():
    try:
        get_akun_donatur = db.session.query(Donatur).all()
        return jsonify({"data": [a.to_dict() for a in get_akun_donatur]}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@donatur.put("/api/put/update/<int:id>")
@jwt_required()
def donatur_update(id):
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")

    try:
        donatur_user = Donatur.query.filter_by(id=id).first()
        if not donatur_user:
            return jsonify({"message": "Donatur tidak ditemukan"}), 404

        cek_email_username = Donatur.query.filter(
            or_(Donatur.email == email, Donatur.username == username),
            Donatur.id != id
        ).first()
        if cek_email_username:
            return jsonify({"message": "Email atau Username sudah digunakan"}), 400

        donatur_user.name = name
        donatur_user.email = email
        donatur_user.username = username
        donatur_user.password = bcrypt.generate_password_hash(password).decode('utf-8')
        db.session.commit()

        return jsonify({"message": "Update berhasil", "user": donatur_user.to_dict()}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@donatur.delete('/api/delete/<int:id>')
@jwt_required()
def donatur_delete(id):
    try:
        donatur_user = Donatur.query.filter_by(id=id).first()
        if not donatur_user:
            return jsonify({"message": "Donatur tidak ditemukan"}), 404

        db.session.delete(donatur_user)
        db.session.commit()
        return jsonify({"message": "Akun donatur berhasil dihapus"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
