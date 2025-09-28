from flask import request, jsonify, Blueprint
from datetime import timedelta
from app.models.user import Admin
from app.extends import db, bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

admin = Blueprint('admin', __name__)


@admin.post('/api/post/login')
def login_admin():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    admin = Admin.query.filter_by(username=username).first()

    if not admin or admin.password != password:
        return jsonify({"message": "Username atau password salah"}), 401
    access_token = create_access_token(identity=str(admin.id),expires_delta=timedelta(hours=1))

    return jsonify(access_token=access_token),200


@admin.put("/api/put/update/<int:id>")
@jwt_required()
def edit_admin(id):
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    try:
        admin_user = Admin.query.filter_by(id=id).first()
        if not admin_user:
            return jsonify({"message": "Admin tidak ditemukan"}), 404

        admin_user.username = username
        if password:  # hanya update kalau ada password baru
            admin_user.password = bcrypt.generate_password_hash(password).decode("utf-8")

        db.session.commit()
        return jsonify({"message": "Update berhasil", "user": admin_user.to_dict()}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@admin.get("/api/get/adminAccount")
@jwt_required()
def get_admin_akun():
    try:
        admin_list = Admin.query.all()
        data_list = [
            {
                "id": a.id,
                "username": a.username,
            } for a in admin_list
        ]
        return jsonify({"admin": data_list}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@admin.get("/api/get/username")
@jwt_required()
def admin_username():
    current_user_id = get_jwt_identity()
    admin_user = Admin.query.get(int(current_user_id))
    if not admin_user:
        return jsonify({"message": "Admin tidak ditemukan"}), 404
    return jsonify({"admin": admin_user.username}), 200
