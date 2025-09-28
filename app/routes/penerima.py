from flask import request, jsonify, Blueprint
from sqlalchemy import or_
from app.models.user import *
import pandas as pd
import joblib
from app.models.klasifikasi import *
from datetime import timedelta
from app.extends import db, bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

penerima = Blueprint('penerima', __name__)
model = joblib.load('./klasifikasi_model.pkl')
@penerima.get('/test')
def index():
    return {"msg": 'ini adalah penerima API'}

@penerima.post("/api/post/login")
def user_login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    try:
        user = Register_login.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            access_token = create_access_token(
                identity={'id': str(user.id), 'role' : user.role},
                expires_delta=timedelta(hours=1)
            )
            user.login_stamp = datetime.now()
            db.session.commit()

            return jsonify({
                "access_token" : access_token,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": user.role
                }
            })
        return jsonify({"message": "Email atau password salah"}), 401
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@penerima.post("/api/post/daftar")
def penerima_daftar():
    data = request.get_json()
    nama = data.get("name")
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")
    role = data.get('role')

    try:
        existing_user = Register_login.query.filter(
            (Register_login.username == username) | (Register_login.email == email) | (Register_login.role == role)
        ).first()

        if existing_user:
            return jsonify({"message": "Email atau Username sudah digunakan"}), 400

        new_user = Register_login(
            name=nama,
            email=email,
            username=username,
            password=bcrypt.generate_password_hash(password).decode('utf-8'),
            role=role
        )
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "Daftar berhasil"}), 201

    except Exception as e:
        return jsonify({"message": str(e)}), 500


@penerima.post("/api/post/personalData")
def penerima_personalData():
    data = request.get_json()
    penghasilan = data.get("penghasilan")
    tanggungan = data.get("tanggungan")
    kendaraan = data.get("kendaraan")
    status_tempat_tinggal = data.get("status_tempat_tinggal")
    jenis_kebutuhan = data.get("jenis_kebutuhan")
    Register_login_id = db.session.query(Register_login).order_by(Register_login.id.desc()).first()
    print(Register_login_id)
    try:
        add_dataDiri = DataDiriPenerima(
            id_penerima=Register_login_id.id,
            penghasilan_perbulan=int(penghasilan),
            jumlah_tanggungan=int(tanggungan),
            jumlah_kendaraan=int(kendaraan),
            status_tempat_tinggal=status_tempat_tinggal,
            jenis_kebutuhan=jenis_kebutuhan
        )
        db.session.add(add_dataDiri)
        db.session.commit()

        assignIdRekomendasi = HasilKlasifikasi(
            id_data_diri_penerima=add_dataDiri.id,
            id_penerima=Register_login_id.id,
        )
        db.session.add(assignIdRekomendasi)
        db.session.commit()
        return jsonify({"message": "Data diri berhasil disimpan"}), 201

    except Exception as e:
        print(e)
        return jsonify({"message": str(e)}), 500

@penerima.get("/api/get/data/account")
@jwt_required()
def get_account():
    get_data = db.session.query(Register_login.id, Register_login.name,
    Register_login.email, Register_login.username,Register_login.password,Register_login.role,Register_login.login_stamp, Register_login.register_stamp,
    DataDiriPenerima.penghasilan_perbulan, 
    DataDiriPenerima.jumlah_tanggungan, DataDiriPenerima.jumlah_kendaraan, 
    DataDiriPenerima.status_tempat_tinggal, DataDiriPenerima.jenis_kebutuhan
    ).join(Register_login, Register_login.id == DataDiriPenerima.id_penerima).all()
    data_list = [
        {
            "id": data[0],
            "name": data[1],
            "email": data[2],
            "username": data[3],
            "password": data[4],
            "role" : data[5],
            "login_stamp": data[6],
            "register_stamp": data[7],
            "penghasilan_perbulan": data[8],
            "jumlah_tanggungan": data[9],
            "jumlah_kendaraan": data[10],
            "status_tempat_tinggal": data[11],
            "jenis_kebutuhan": data[12]
        }
        for data in get_data
    ]
    return jsonify({"data" : data_list}), 200


@penerima.get("/api/get/data/personal")
@jwt_required()
def get_personal():
    try:
        get_data = db.session.query(DataDiriPenerima.id , 
        Register_login.name,
        DataDiriPenerima.penghasilan_perbulan,
        DataDiriPenerima.jumlah_tanggungan,
        DataDiriPenerima.jumlah_kendaraan,
        DataDiriPenerima.status_tempat_tinggal,
        DataDiriPenerima.jenis_kebutuhan
        ).join(Register_login, Register_login.id == DataDiriPenerima.id_penerima).all()
        data_list = [
            {
                "id": data[0],
                "name": data[1],
                "penghasilan_perbulan": data[2],
                "jumlah_tanggungan": data[3],
                "jumlah_kendaraan": data[4],
                "status_tempat_tinggal": data[5],
                "jenis_kebutuhan": data[6]
            }
            for data in get_data
        ]
        return jsonify({
            "data": data_list,
        })
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@penerima.get("/api/get/data")
def penerima_personal():
    try:
        data = db.session.query(DataDiriPenerima).all()
        return jsonify({
            "data": [d.to_dict() for d in data]
        })
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    


@penerima.put("/api/put/update/<int:id>")
@jwt_required()
def penerima_update(id):
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")

    try:
        penerima_user = Register_login.query.filter_by(id=id).first()
        if not penerima_user:
            return jsonify({"message": "Penerima tidak ditemukan"}), 404

        cek_email_username = Register_login.query.filter(
            or_(Register_login.email == email, Register_login.username == username),
            Register_login.id != id
        ).first()
        if cek_email_username:
            return jsonify({"message": "Email atau Username sudah digunakan"}), 400

        penerima_user.name = name
        penerima_user.email = email
        penerima_user.username = username
        penerima_user.password = bcrypt.generate_password_hash(password).decode('utf-8')
        penerima_user.role = "penerima"
        db.session.commit()

        return jsonify({"message": "Update berhasil"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@penerima.delete("/api/delete/<int:id>")
@jwt_required()
def penerima_delete(id):
    current_user = get_jwt_identity()
    try:
        if current_user['role'] != 'admin':
            return jsonify({
                'message' : 'Akses ditolak, hanya admin yng bisa hapus data'
            })
        user = Register_login.query.get(id)
        if not user:
            return jsonify({"message": "Penerima tidak ditemukan"}), 404
        if user.role != 'penerima':
            return jsonify({'message' : 'role bukan penerima'})
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "Akun penerima berhasil dihapus"}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

@penerima.get('/api/get/informasiDonasi')
@jwt_required()
def get_informasiDonasi():
    id = get_jwt_identity()
    try:
        data = db.session.query(Register_login.id, Register_login.name,Donasi.tanggal_donasi,Barang.gambar_barang,DataDiriPenerima.jenis_kebutuhan).join(Register_login, Register_login.id == Donasi.id_penerima).join(
            Barang, Barang.id == Donasi.id_barang).join(
            DataDiriPenerima, DataDiriPenerima.id_penerima == id).all()
        data_list = [
            {
                "id": d[0],
                "name": d[1],
                "tanggal_donasi": d[2].isoformat() if d[2] else None,
                "gambar_barang": f"http://localhost:5000/barang/api/get/uploads/{d[3]}" if d[3] else None,
                "jenis_kebutuhan": d[4]
            } for d in data
        ]
        return jsonify({"data": data_list}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@penerima.put("/api/update/personalDataDiri")
@jwt_required
def update_personalDataDiri():
    id = get_jwt_identity
    data = request.get_json()
    penghasilan_perbulan = data.get('penghasilan_perbulan')
    jumlah_tanggungan = data.get('jumlah_tanggungan')
    jumlah_kendaraan = data.get('jumlah_kendaraan')
    status_tempat_tinggal = data.get('status_tempat_tinggal')
    jenis_kebutuhan = data.get('jenis_kebutuhan')
    try:
        personal = DataDiriPenerima.query.filter_by(id=id).first()
        personal.penghasilan_perbulan = penghasilan_perbulan
        personal.jumlah_tanggungan = jumlah_tanggungan
        personal.jumlah_kendaraan = jumlah_kendaraan
        personal.status_tempat_tinggal = status_tempat_tinggal
        personal.jenis_kebutuhan = jenis_kebutuhan
        db.session.commit()

        return jsonify({
            'message' : 'update berhasil'
        }),200

    except Exception as a:
        return jsonify({"message": str(a)}), 500
    
@penerima.get('/api/get/username')
@jwt_required()
def get_username():
    try:
        current_user_id = get_jwt_identity()
        penerima = Register_login.query.get(int(current_user_id))

        if not penerima:
            return jsonify({"message": "Penerima tidak ditemukan"}), 404

        return jsonify({
            "username": penerima.username,
            "email": penerima.email
        }), 200
    except Exception as e:
        return jsonify({"message": "Terjadi kesalahan", "error": str(e)}), 500

        




