from flask import request, jsonify, current_app, Blueprint
from werkzeug.utils import secure_filename
import os
from sqlalchemy.orm import aliased
from app.models.user import *
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from flask import send_from_directory

donasi = Blueprint('donasi', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@donasi.post('/api/post/donate/<int:id_penerima>')
@jwt_required()
def donate(id_penerima):
    id_donatur = get_jwt_identity()
    try:
        name_barang = request.form.get('name_barang')
        if not name_barang:
            return jsonify({"error": "Nama barang wajib diisi"}), 400

        if 'gambar_barang' not in request.files:
            return jsonify({"error": "No file part"}), 400

        gambar_barang = request.files['gambar_barang']
        if gambar_barang.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if not allowed_file(gambar_barang.filename):
            return jsonify({"error": "File tidak diizinkan"}), 400

        filename = secure_filename(gambar_barang.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        gambar_barang.save(filepath)

        barang = Barang(
            nama_barang=name_barang,
            gambar_barang=filename,
            id_donatur=id_donatur,
            tanggal_masuk=None
        )
        db.session.add(barang)
        db.session.commit()

        donasi_entry = Donasi(
            id_donatur=id_donatur,
            id_penerima=id_penerima,
            id_barang=barang.id,
            tanggal_donasi=datetime.now()
        )
        db.session.add(donasi_entry)
        db.session.commit()

        return jsonify({"message": "Donasi berhasil"}), 201

    except Exception as e:
        print(e)
        return jsonify({"message": str(e)}), 500


@donasi.put("/api/put/approve/<int:id>")
@jwt_required()
def approve_donasi(id):
    try:
        donasi = Donasi.query.get(id)

        if not donasi:
            return jsonify({"message": "Donasi tidak ditemukan"}), 404

        donasi.status = "approved"
        donasi.tanggal_approve = datetime.now()
        db.session.commit() 

        barang = Barang.query.filter(Barang.id == donasi.id_barang).first()
        if barang:
            barang.tanggal_masuk = donasi.tanggal_approve
            db.session.commit() 
        return jsonify({"message": "donasi berhasil diapprove"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    
@donasi.put("/api/reject/<int:id>")
@jwt_required()
def delete_donasi(id):
    try:
        donasi = Donasi.query.get(id)

        if not donasi:
            return jsonify({"message": "Donasi tidak ditemukan"}), 404
        
        donasi.status = "rejected"
        db.session.commit()

        return jsonify({"message": "donasi ditolak"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@donasi.get("/api/get/donasi")
@jwt_required()
def get_all_data():
    try:
        Donatur = aliased(Register_login)
        Penerima = aliased(Register_login)
        donasi_query = (
            db.session.query(
                Donasi.id,
                Donatur.name.label("donatur_name"),
                Penerima.name.label("penerima_name"),
                Barang.nama_barang,
                Donasi.tanggal_donasi,
                Donasi.status,
                Donasi.tanggal_approve,
            )
            .join(Donatur, Donasi.id_donatur == Donatur.id)
            .join(Penerima, Donasi.id_penerima == Penerima.id)
            .outerjoin(Barang, Donasi.id_barang == Barang.id)
            .all()
        )

        donasi_riwayat = [
            {
                "id": d[0],
                "donatur": d[1],
                "penerima": d[2],
                "barang": d[3],
                "tanggal_donasi": d[4].isoformat() if d[4] else None,
                "status": d[5],
                "tanggal_approve": d[6].isoformat() if d[6] else None,
            }
            for d in donasi_query
        ]

        return jsonify({"donasi": donasi_riwayat}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@donasi.delete('/api/delete/<int:id>')
@jwt_required()
def donasi_delete(id):
    try:
        donasi_user = Donasi.query.get(id)
        if not donasi_user:
            return jsonify({"message": "donasi tidak ditemukan"}), 404
        db.session.delete(donasi_user)
        db.session.commit()
        return jsonify({"message": "item berhasil dihapus"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500