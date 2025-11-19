from flask import request, jsonify, current_app, Blueprint
from werkzeug.utils import secure_filename
import os
from sqlalchemy.orm import aliased
from app.models.user import *
from app.models.notifikasi import *
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from flask import send_from_directory
from sqlalchemy.orm import aliased
from sqlalchemy.orm import aliased
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.extends import socketio

donasi = Blueprint('donasi', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg','avif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@donasi.post('/api/post/donate/<int:id_user>')
@jwt_required()
def donate(id_user):
    print(id_user)
    id = get_jwt_identity()
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
            kondisi_barang=int(request.form.get('kondisi_barang')),
            id_donatur=id,
            tanggal_masuk=None
        )
        db.session.add(barang)
        db.session.commit()

        donasi_entry = Donasi(
            id_donatur=id,
            id_penerima=id_user,
            id_barang=barang.id,
            tanggal_donasi=datetime.now()
        )
        db.session.add(donasi_entry)
        db.session.commit()

        # getPersonal = db.session(DataDiriPenerima).get(id)


        # getPersonal.jumlah = request.form.get('jumlah')
        # db.session.commit()

        socketio.emit('data_update',  {'message': 'Donasi diperbarui'})
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
            return jsonify({"message": "Belum ada yang donasi"}), 404

        donasi.status = "approved"
        donasi.tanggal_approve = datetime.now()
        db.session.commit() 

        if donasi.status == 'approved':
            donasi.status_pengiriman = 'delivering'
            db.session.commit()

        barang = Barang.query.filter_by(id=donasi.id_barang).first()
        if barang:
            barang.tanggal_masuk = donasi.tanggal_approve
            db.session.commit() 
        socketio.emit('data_update',  {'message': 'Donasi diperbarui'})
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
        donasi.tanggal_reject = datetime.now()
        db.session.commit()

        if donasi.status == 'rejected':
            donasi.status_pengiriman = 'rejected'
            db.session.commit()
        socketio.emit('data_update',  {'message': 'Donasi diperbarui'})
        return jsonify({"message": "donasi ditolak"}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": str(e)}), 500

@donasi.put('/api/done/<int:id>')
@jwt_required()
def update_donasi(id):
    
    try:
        doneDonasi = Donasi.query.get(id)
        
        if not doneDonasi:
            return jsonify({'message':'Donasi tidak ditemukan'})
        
        doneDonasi.status_pengiriman = 'done'
        db.session.commit()
        socketio.emit('data_update',  {'message': 'Donasi diperbarui'})
        return jsonify({'message': 'donasi diselesaikan'})

    except Exception as e:
        print(e)
        return jsonify({'error' : str(e)}),500


@donasi.get("/api/get/donasi")
@jwt_required()
def get_all_data():
    try:
        # Buat alias untuk tabel Register_login
        Donatur = aliased(Register_login)
        Penerima = aliased(Register_login)

        # Query utama
        donasi_query = (
            db.session.query(
                Donasi.id,
                Donatur.name.label("donatur_name"),
                Penerima.name.label("penerima_name"),
                Barang.nama_barang,
                Barang.kondisi_barang,
                Donasi.tanggal_donasi,
                Donasi.status,
                Donasi.tanggal_approve,
                Donasi.tanggal_reject,
                DataDiriPenerima.jumlah,
                Notifikasi.pesan,
            )
            .join(Donatur, Donatur.id == Donasi.id_donatur)
            .outerjoin(Penerima, Penerima.id == Donasi.id_penerima)
            .outerjoin(Barang, Barang.id == Donasi.id_barang)
            .outerjoin(DataDiriPenerima, DataDiriPenerima.id_user == Donasi.id_penerima)
            # Penting: perbaiki relasi dengan Notifikasi
            .outerjoin(Notifikasi, Notifikasi.id_donasi == Donasi.id)
            .order_by(Donasi.id.asc())
            .all()
        )

        # Buat daftar hasil JSON
        donasi_riwayat = [
            {
                "id": d.id,
                "donatur_name": d.donatur_name,
                "penerima_name": d.penerima_name or "Belum Ada",
                "barang": d.nama_barang,
                "kondisi_barang": d.kondisi_barang,
                "jumlah": d.jumlah,
                "tanggal_donasi": d.tanggal_donasi.isoformat() if d.tanggal_donasi else None,
                "status": d.status,
                "pesan": d.pesan,
                "tanggal_approve": d.tanggal_approve.isoformat() if d.tanggal_approve else None,
                "tanggal_reject": d.tanggal_reject.isoformat() if d.tanggal_reject else None,
            }
            for d in donasi_query
        ]

        return jsonify({"donasi": donasi_riwayat}), 200

    except Exception as e:
        print("❌ ERROR:", e)
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
        socketio.emit('data_update',  {'message': 'Donasi diperbarui'})
        return jsonify({"message": "item berhasil dihapus"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@donasi.get('/api/get/riwayatDonasi')
@jwt_required()
def riwayat_donasi():
    Penerima = aliased(Register_login)
    try:
        riwayat = db.session.query(
            Donasi.id,
            Penerima.name,
            Barang.nama_barang,
            DataDiriPenerima.kategori,
            Barang.kondisi_barang,
            DataDiriPenerima.jumlah,
            Donasi.tanggal_donasi,
            Donasi.status,
            Donasi.tanggal_approve,
            Donasi.tanggal_reject,
            Notifikasi.pesan,
            Donasi.status_pengiriman
        ).join(Barang, Donasi.id_barang == Barang.id
        ).outerjoin(Notifikasi, Notifikasi.id_donasi == Donasi.id
        ).outerjoin(Penerima, Penerima.id == Donasi.id_penerima
        ).outerjoin(DataDiriPenerima, DataDiriPenerima.id_user == Donasi.id_penerima
        ).filter(Donasi.id_donatur == get_jwt_identity()
        ).order_by(Donasi.id.desc()
        ).all()
        riwayat_list = [
            {
                "id": r.id,
                "name" : r.name,
                "nama_barang": r.nama_barang,
                "kategori": r.kategori,
                "kondisi" : r.kondisi_barang,
                "jumlah": r.jumlah,
                "tanggal_donasi": r.tanggal_donasi.isoformat() if r.tanggal_donasi else None,
                "status": r.status,
                "tanggal_approve": r.tanggal_approve.isoformat() if r.tanggal_approve else None,
                "tanggal_reject": r.tanggal_reject.isoformat() if r.tanggal_reject else None,
                "pesan": r.pesan,
                "status_pengiriman" : r.status_pengiriman
            }
            for r in riwayat
        ]
        return jsonify({"riwayat": riwayat_list}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

@donasi.get('/api/get/Kategori/<kategori>')
@jwt_required()
def getKategori(kategori):
    try:
        dataKategori = (
            DataDiriPenerima.query.filter(DataDiriPenerima.kategori == kategori).all()
        )

        kategori_list = [row.kategori for row in dataKategori]
        return jsonify({'kategori': kategori_list}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500



@donasi.get('/api/get/donasiTerbaru')
@jwt_required()
def donasi_terbaru_penerima():
    try:
        Donatur = aliased(Register_login)
        Penerima = aliased(Register_login)

        barangTerbaru = (
            db.session.query(
                Donasi.id,
                Barang.nama_barang,
                Donatur.name.label('donatur_name'),
                DataDiriPenerima.jumlah,
                Barang.kondisi_barang,
                DataDiriPenerima.kategori,
                Donasi.tanggal_donasi,
                Donasi.status,
                Donasi.status_pengiriman
            )
            .join(Barang, Donasi.id_barang == Barang.id)
            .outerjoin(Donatur, Donasi.id_donatur == Donatur.id)
            .outerjoin(Penerima, Donasi.id_penerima == Penerima.id)
            .outerjoin(DataDiriPenerima, DataDiriPenerima.id_user == Penerima.id)
            .filter(Donasi.id_penerima == get_jwt_identity()) 
            .order_by(Donasi.id.desc())
            .all()
        )

        riwayat_terbaru = [
            {
                "id": i.id,
                "nama_barang": i.nama_barang,
                "kategori": i.kategori,
                "donatur_name": i.donatur_name,
                "jumlah": i.jumlah,
                "kondisi": i.kondisi_barang,
                "tanggal_donasi": i.tanggal_donasi.strftime("%Y-%m-%d"),
                "status": i.status,
                "status_pengiriman" : i.status_pengiriman
            }
            for i in barangTerbaru
        ]
        return jsonify({'donasi': riwayat_terbaru}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500



