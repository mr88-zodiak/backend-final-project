from flask import request, jsonify,make_response, Blueprint
from sqlalchemy import or_
from app.models.user import *
import pandas as pd
import joblib
from config import Config
from app.models.klasifikasi import *
from datetime import datetime
from app.extends import db, bcrypt,socketio
from flask_jwt_extended import create_access_token,create_refresh_token, jwt_required, get_jwt_identity,set_refresh_cookies
from functools import wraps
from flask_cors import CORS
from sqlalchemy import and_
# from flask_socketio import socketio.emit


user = Blueprint('user', __name__)
model = joblib.load('./klasifikasi_model.pkl')

@user.get('/test')
def index():
    return {"msg": 'ini adalah penerima API'}

@user.post("/api/post/login")
def user_login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    try:
        user = Register_login.query.filter_by(email=email).first()

        if user is None:
            return jsonify({"message": "Email atau password belum terdaftar"}), 401

        if not bcrypt.check_password_hash(user.password, password):
            return jsonify({"message": "Email atau password salah"}), 401

        cekDataDiri = DataDiriPenerima.query.filter_by(id_user=user.id).first()

        # Buat access token & refresh token
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role},
            expires_delta=Config.JWT_ACCESS_TOKEN_EXPIRES
        )
        refresh_token = create_refresh_token(
            identity=str(user.id),
            additional_claims={"role": user.role},
            expires_delta=Config.JWT_REFRESH_TOKEN_EXPIRES
        )

        # update login_stamp
        user.login_stamp = datetime.now()
        db.session.commit()

        # pakai make_response untuk set cookie refresh token
        resp = make_response(jsonify({
            "access_token": access_token,
            "user": {
                "id": user.id,
                "dataDiriId": cekDataDiri.id if cekDataDiri else None,
                "email": user.email,
                "role": user.role
            }
        }))
        set_refresh_cookies(resp, refresh_token)
        return resp

    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"message": str(e)}), 500

@user.post("/api/post/daftar")
def penerima_daftar():
    data = request.get_json()
    nama = data.get("name")
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")
    role = data.get('role')

    try:
        existing_user = Register_login.query.filter(
            (Register_login.username == username) | (Register_login.email == email) 
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

        return jsonify({"message": "Daftar berhasil",
                        'user': role}), 201

    except Exception as e:
        return jsonify({"message": str(e)}), 500

@user.post("/api/post/personalData")
@jwt_required()
def penerima_personalData():
    data = request.get_json()
    penghasilan = data.get("penghasilan")
    tanggungan = data.get("tanggungan")
    kendaraan = data.get("kendaraan")
    status_tempat_tinggal = data.get("status_tempat_tinggal")
    jenis_kebutuhan = data.get("jenis_kebutuhan")
    jumlah = data.get('jumlah')
    kategori = data.get('kategori')
    alamat = data.get('alamat')
    print(get_jwt_identity())
    try:
        user = Register_login.query.get(get_jwt_identity())
        if user.role != 'penerima':
            return jsonify({'message': 'role bukan penerima'}), 401

        if DataDiriPenerima.query.filter_by(id_user=user.id).first():
            return jsonify({"message": "Data diri sudah ada"}), 400

        add_dataDiri = DataDiriPenerima(
            id_user=user.id,
            penghasilan_perbulan=int(penghasilan),
            jumlah_tanggungan=int(tanggungan),
            jumlah_kendaraan=int(kendaraan),
            status_tempat_tinggal=status_tempat_tinggal,
            jenis_kebutuhan=jenis_kebutuhan,
            jumlah=jumlah,
            # alamat=alamat,
            kategori=kategori
        )
        db.session.add(add_dataDiri)
        db.session.commit()

        assignIdRekomendasi = HasilKlasifikasi(
            id_data_diri=add_dataDiri.id,
            id_user=user.id
        )
        db.session.add(assignIdRekomendasi)
        db.session.commit()

        return jsonify({"message": "Data diri berhasil disimpan"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@user.post("/api/post/modal/personal")
def penerima_personalData_modal():
    data = request.get_json()
    penghasilan = data.get("penghasilan")
    tanggungan = data.get("tanggungan")
    kendaraan = data.get("kendaraan")
    status_tempat_tinggal = data.get("status_tempat_tinggal")
    jenis_kebutuhan = data.get("jenis_kebutuhan")
    jumlah = data.get('jumlah')
    kategori = data.get("kategori")
    alamat = data.get('alamat')
    try:
        user = db.session.query(Register_login).order_by(Register_login.id.desc()).first()
        print(user.role)
        print(user.id)
        if user.role != 'penerima':
            return jsonify({'message': 'role bukan penerima'}), 401

        if DataDiriPenerima.query.filter_by(id_user=user.id).first():
            return jsonify({"message": "Data diri sudah ada"}), 400

        add_dataDiri = DataDiriPenerima(
            id_user=user.id,
            penghasilan_perbulan=int(penghasilan),
            jumlah_tanggungan=int(tanggungan),
            jumlah_kendaraan=int(kendaraan),
            status_tempat_tinggal=status_tempat_tinggal,
            jenis_kebutuhan=jenis_kebutuhan,
            jumlah=jumlah,
            # alamat=alamat,
            kategori=kategori
        )
        db.session.add(add_dataDiri)
        db.session.commit()

        assignIdRekomendasi = HasilKlasifikasi(
            id_data_diri=add_dataDiri.id,
            id_user=user.id
        )
        db.session.add(assignIdRekomendasi)
        db.session.commit()
        socketio.emit('data_update',  {'message': 'Donasi diperbarui'})
        return jsonify({"message": "Data diri berhasil disimpan"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@user.get('/api/get/account/donatur')
@jwt_required()
def getDonatur():
    getData = Register_login.query.filter_by(role='donatur').order_by(Register_login.id.asc()).all()
    return jsonify({"data": [a.to_dict() for a in getData]}), 200


@user.get("/api/get/account/penerima")
@jwt_required()
def get_account():
    get_data = (
        db.session.query(
            Register_login.id,
            Register_login.name,
            Register_login.email,
            Register_login.username,
            Register_login.password,
            Register_login.role,
            Register_login.status,
            Register_login.login_stamp,
            Register_login.register_stamp,
            Register_login.approved_date,
            Register_login.rejected_date,
            DataDiriPenerima.penghasilan_perbulan,
            DataDiriPenerima.jumlah_tanggungan,
            DataDiriPenerima.jumlah_kendaraan,
            DataDiriPenerima.status_tempat_tinggal,
            DataDiriPenerima.kategori,
            DataDiriPenerima.jenis_kebutuhan,
            DataDiriPenerima.jumlah
        )
        .join(DataDiriPenerima)
        .filter(Register_login.role == "penerima")
        .order_by(Register_login.id.asc()).all()
    )

    data_list = [
        {
            "id": data[0],
            "name": data[1],
            "email": data[2],
            "username": data[3],
            "password": data[4],
            "role": data[5],
            "status" : data[6],
            "login_stamp": data[7],
            "register_stamp": data[8],
            "approved_date" : data[9],
            "rejected_date" : data[10],
            "penghasilan_perbulan": data[11],
            "jumlah_tanggungan": data[12],
            "jumlah_kendaraan": data[13],
            "status_tempat_tinggal": data[14],
            "kategori": data[15],
            "jenis_kebutuhan": data[16],
            "jumlah" : data[17]
        }
        for data in get_data
    ]

    return jsonify({"data": data_list}), 200



@user.get("/api/get/data/personal")
@jwt_required()
def get_personal():
    try:
        get_data = db.session.query(DataDiriPenerima.id , 
        Register_login.name,
        DataDiriPenerima.penghasilan_perbulan,
        DataDiriPenerima.jumlah_tanggungan,
        DataDiriPenerima.jumlah_kendaraan,
        DataDiriPenerima.status_tempat_tinggal,
        DataDiriPenerima.kategori,
        DataDiriPenerima.jenis_kebutuhan,
        DataDiriPenerima.jumlah
        ).join(Register_login).filter_by(role='penerima').order_by(Register_login.id.asc()).all()
        data_list = [
            {
                "id": data[0],
                "name": data[1],
                "penghasilan_perbulan": data[2],
                "jumlah_tanggungan": data[3],
                "jumlah_kendaraan": data[4],
                "status_tempat_tinggal": data[5],
                "kategori": data[6],
                "jenis_kebutuhan": data[7],
                "jumlah": data[8]
            }
            for data in get_data
        ]
        return jsonify({
            "data": data_list,
        })
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@user.get("/api/get/data")
def penerima_personal():
    try:
        data = db.session.query(DataDiriPenerima).all()
        return jsonify({
            "data": [d.to_dict() for d in data]
        })
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    


@user.put("/api/put/update/<int:id>")
@jwt_required()
def penerima_update(id):
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")
    role = data.get('role')
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
        penerima_user.role = role
        db.session.commit()
        socketio.emit('data_update',  {'message': 'Donasi diperbarui'})
        return jsonify({"message": "Update berhasil"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@user.delete("/api/delete/penerima/<int:id>")
@jwt_required()
def penerima_delete(id):
    try:
        db.session.query(Register_login).filter(and_(Register_login.id == id, Register_login.role == 'penerima')
        ).delete()
        db.session.commit()
        socketio.emit('data_update',  {'message': 'Donasi diperbarui'})
        return jsonify({"message": "Akun penerima berhasil dihapus"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500
@user.delete('/api/delete/donatur/<int:id>')
@jwt_required()
def donatur_delete(id):
    try:
        db.session.query(Register_login).filter(
            and_(Register_login.id == id, Register_login.role == 'donatur')
        ).delete()
        db.session.commit()
        socketio.emit('data_update',  {'message': 'Donasi diperbarui'})
        return jsonify({'message' : 'Akun donatur berhasil dihapus'}),200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}),500
@user.get('/api/get/informasiDonasi')
@jwt_required()
def get_informasiDonasi():
    id = get_jwt_identity()
    try:
        data = db.session.query(Register_login.id, Register_login.name,Donasi.tanggal_donasi,Barang.gambar_barang,DataDiriPenerima.jenis_kebutuhan).join(Register_login, Register_login.id == Donasi.id_user).join(
            Barang, Barang.id == Donasi.id_barang).join(
            DataDiriPenerima, DataDiriPenerima.id_user == id).all()
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

@user.put("/api/put/personalDataDiri/<int:id>")
@jwt_required()
def update_personalDataDiri(id):
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

        socketio.emit('data_update',  {'message': 'Donasi diperbarui'})
        return jsonify({
            'message' : 'update berhasil'
        }),200

    except Exception as a:
        db.session.rollback()
        return jsonify({"message": str(a)}), 500
    
@user.get('/api/get/username')
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

@user.get('/api/get/role/user')
@jwt_required()
def get_role():
    try:
        data_role = db.session.query(Register_login).order_by(Register_login.id.asc()).all()
        return jsonify({'data' : [a.to_dict() for a in data_role]})
    except Exception as e:
        print(e)
        return jsonify({'message': 'Terjadi kesalah pada internal server ' + e}),500
    
@user.put('/api/user/approved/<int:id>')
@jwt_required()
def user_approved(id):
    try:
        approved = Register_login.query.get(id)

        if not approved:
            return jsonify({'message': 'belum ada yang di approve'}),404
        approved.status = 'approved'
        approved.approved_date = datetime.now()
        db.session.commit()
        socketio.emit('data_update',  {'message': 'Donasi diperbarui'})
        return jsonify({'message': 'user berhasil di approved'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}),500

@user.put('/api/user/rejected/<int:id>')
@jwt_required()
def user_rejected(id):
    try:
        reject = Register_login.query.get(id)
        if not reject:
            return jsonify({'message' : 'belum ada yang di reject'})
        reject.rejected_date = datetime.now()
        reject.status = 'rejected'
        db.session.commit()
        socketio.emit('data_update',  {'message': 'Donasi diperbarui'})
        return jsonify({'message' : 'user berhasil di reject'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message' : str(e)}),500

@user.post('/oauth/token')
@jwt_required(refresh=True, locations=["cookies"])
def refresh_token():
    try:
        current_user_id = get_jwt_identity()
        user = Register_login.query.get(int(current_user_id))

        if not user:
            return jsonify({"message": "User tidak ditemukan"}), 404

        new_access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role},
            expires_delta=Config.JWT_ACCESS_TOKEN_EXPIRES  # perbaikan
        )

        return jsonify({
            "access_token": new_access_token
        }), 200

    except Exception as e:
        return jsonify({"message": "Terjadi kesalahan", "error": str(e)}), 500
