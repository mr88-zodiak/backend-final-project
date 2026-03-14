from flask import request, jsonify
from app.models.user import *
from app.models.pengajuan import *
from flask import Blueprint
from sqlalchemy.orm import aliased
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask import send_from_directory,current_app
# from flask_socketio import socketio.emit
from app.extends import socketio
barang = Blueprint('barang', __name__)


@barang.get('/api/get/uploads/<filename>')
def get_uploaded_file(filename):
    # print("UPLOAD_FOLDER:", current_app.config['UPLOAD_FOLDER'])
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@barang.get('/api/get/barang')
# @jwt_required()
def get_barang():
    Donatur = aliased(Register_login)
    Penerima = aliased(Register_login)
    try:
        barang = db.session.query(
            Donatur.id,
            Barang.id,       
            Donatur.name,          
            Barang.nama_barang,
            Barang.kondisi_barang,     
            Barang.gambar_barang,   
            Barang.tanggal_masuk,
            Donasi.status,
            Donasi.status_pengiriman   
        ).outerjoin(Donasi, Barang.id == Donasi.id_barang 
        ).join(Donatur, Barang.id_donatur == Donatur.id).order_by(Barang.id.asc()).all()

        detail_barang = [
            {
                "id": a[0],
                "barangId": a[1],                   
                "donaturName": a[2],           
                "barangName": a[3], 
                "kondisi_barang": a[4],           
                "gambar": f"http://localhost:5000/barang/api/get/uploads/{a[5]}" if a[5] else None,
                "tanggal_masuk": a[6],
                "status": a[7],
                "status_pengiriman": a[8]  
            } for a in barang
        ]

        return jsonify({"barang": detail_barang}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": str(e)}), 500

@barang.delete('/api/delete/<int:id>')
@jwt_required()
def barang_delete(id):
    try:
        barang_user = Barang.query.filter_by(id=id).first()
        if not barang_user:
            return jsonify({"message": "barang tidak ditemukan"}), 404
        db.session.delete(barang_user)
        db.session.commit()
        socketio.emit('data_update',  {'message': 'Donasi diperbarui'})
        return jsonify({"message": "item berhasil dihapus"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500
    
@barang.get("/api/get/barang/<int:id>")
def getDonasi(id):
    data = db.session.query(pengajuanBarang.nama_barang).filter_by(id_penerima=id).first()
    try:
        if data:
            return jsonify({"data": data.nama_barang}), 200
        else:
            return jsonify({"message": "Data not found"}), 404
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500