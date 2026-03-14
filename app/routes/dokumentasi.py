from flask import Blueprint, request, jsonify, send_from_directory, current_app
from app.models.Modelsdokumentasi import Dokumentasi
from app.models.user import *
from app.extends import db
from config import Config
from flask_jwt_extended import jwt_required
from PIL import Image
from datetime import datetime
from app.extends import socketio
from werkzeug.utils import secure_filename
import os

dokumentasi = Blueprint('dokumentasi', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@dokumentasi.get('/api/get/uploads/<filename>')
def get_uploaded_file(filename):
    # print("UPLOAD_FOLDER:", current_app.config['UPLOAD_FOLDER'])
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@dokumentasi.post("/api/post/dokumentasi/<int:id>")
@jwt_required()
def buatDokumentasi(id):
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file_dokumentasi = request.files['file']

        if file_dokumentasi.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if not allowed_file(file_dokumentasi.filename):
            return jsonify({"error": "File tidak diizinkan"}), 400

        filename = secure_filename(file_dokumentasi.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        # --- COMPRESS GAMBAR ---
        img = Image.open(file_dokumentasi)

        # compress (quality 70 biar kecil)
        img.save(filepath, optimize=True, quality=70)

        # --- DAPATKAN UKURAN ---
        size_bytes = os.path.getsize(filepath)
        size_kb = size_bytes / 1024
        size_mb = size_bytes / (1024 * 1024)

        ukuran_file = f"{size_kb:.2f} KB ({size_mb:.2f} MB)"
        
        woyDokumentasikan_lah = Dokumentasi(
            id_donatur=id,
            file=filename,       
            file_name=filename,
            ukuran_file=ukuran_file,
            tanggal_dokumentasi=datetime.now()
        )
        db.session.add(woyDokumentasikan_lah)
        db.session.commit()
        dbStatus = Donasi.query.filter_by(id_donatur=id).first()
        if dbStatus is None:
            return jsonify({'error' : 'Donasi not found'}), 404
        dbStatus.status_pengiriman = 'done'
        db.session.commit()
        socketio.emit('data_update',  {'message': 'Dokumentasi baru ditambahkan'})
        return jsonify({"message": "Berhasil upload"}), 201

    except Exception as e:
        print("ERROR:", e)
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@dokumentasi.get("/api/get/dokumentasi")
@jwt_required()
def getDokumentasi():
    try:
        dokumentasi_list = db.session.query(Dokumentasi.id,Dokumentasi.file,Dokumentasi.file_name,
            Dokumentasi.ukuran_file,
            Dokumentasi.tanggal_dokumentasi,Register_login.name).join(
                Dokumentasi, Register_login.id == Dokumentasi.id_donatur
            ).where(Register_login.role == 'donatur').all()
        data_list = [
            {
                "id" : a[0],
                "file" : a[1],
                "file_name" : f"http://localhost:5000/dokumentasi/api/get/uploads/{a[2]}" if a[2] else None,
                "ukuran_file" : a[3],
                "tanggal_dokumentasi" : a[4],
                "donatur_name" : a[5]
            } for a in dokumentasi_list
        ]
        return jsonify({'dokumentasi' : data_list}),200
    except Exception as e: 
        print("ERROR:", e)
        return jsonify({'error' : str(e)}),500
    

@dokumentasi.delete("/api/delete/dokumentasi/<int:id>")
@jwt_required()
def deleteDokumentasi(id):
    try:
        dokumentasi_item = Dokumentasi.query.filter_by(id=id).first()
        if not dokumentasi_item:
            return jsonify({"message" : "maaf dokumentasi tidak ditemukan"}),404
        db.session.delete(dokumentasi_item)
        db.session.commit()
        socketio.emit('data_update',  {'message': 'Dokumentasi dihapus'})
        return jsonify({'message': "dokumentasi berhasil dihapus"})
    except Exception as e:
        db.session.rollback()
        print("ERROR: ", e)
        return jsonify({"error": str(e)}),500