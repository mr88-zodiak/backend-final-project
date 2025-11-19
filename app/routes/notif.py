from flask import request, jsonify, Blueprint
from app.models.user import *
from app.models.notifikasi import Notifikasi
from app.extends import db
from sqlalchemy.orm import aliased
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.extends import socketio

notif = Blueprint('notif', __name__)

@notif.post('/api/post/notif/<int:id_barang>')
@jwt_required()
def create_notif(id_barang):
    try:
        data = request.get_json()
        message = data.get('message')
        if not message:
            return jsonify({"error": "Message is required"}), 400
        donasi = Donasi.query.filter_by(id_barang=id_barang).first()
        barang = Barang.query.get(id_barang)

        new_notif = Notifikasi(
            id_barang=id_barang,   
            id_donasi=donasi.id if donasi else None,
            id_donatur=barang.id_donatur if barang else None,
            pesan=message,               
        )

        db.session.add(new_notif)
        db.session.commit()
        socketio.emit('data_update',  {'message': 'Donasi diperbarui'})
        return jsonify({"message": "alasan anda masuk akal juga"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@notif.get('/api/get/notif')
@jwt_required()
def get_notifs():
    try:
        notifs =  db.session.query(
        Barang.nama_barang, 
        Donasi.status, 
        Donasi.tanggal_donasi
        ).join(Donasi, Barang.id == Donasi.id_barang
        ).filter(Donasi.id_donatur == get_jwt_identity()).order_by(Donasi.id.desc()).all()

        notif_list = [
            {
                "nama_barang": n.nama_barang,
                "status": n.status,
                "tanggal_donasi": n.tanggal_donasi.isoformat() if n.tanggal_donasi else None,
            }
            for n in notifs
        ]

        return jsonify({"notifications": notif_list}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@notif.get('/api/get/data/notif')
@jwt_required()
def get_data_notifs():
    try:
        dataNotif = db.session.query(Donasi.id, 
        Register_login.name,
        Barang.nama_barang,
        Donasi.tanggal_donasi,
        Donasi.status).join(Register_login, Register_login.id == Donasi.id_donatur
        ).join(Barang, Donasi.id_barang == Barang.id
        ).filter(Donasi.id_donatur == get_jwt_identity()).order_by(Donasi.id.desc()
        ).all()

        notif_list = [
            {
                "nama_barang": n.nama_barang,
                "status": n.status,
                "tanggal_donasi": n.tanggal_donasi.isoformat() if n.tanggal_donasi else None,
            }
            for n in dataNotif
        ]

        return jsonify({"notifications": notif_list}), 200
    
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500
