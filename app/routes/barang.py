from flask import request, jsonify
from app.models.user import *
from flask import Blueprint
from sqlalchemy.orm import aliased
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask import send_from_directory,current_app
barang = Blueprint('barang', __name__)


@barang.get('/api/get/uploads/<filename>')
def get_uploaded_file(filename):
    # print("UPLOAD_FOLDER:", current_app.config['UPLOAD_FOLDER'])
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@barang.get('/api/get/barang')
@jwt_required()
def get_barang():
    Donatur = aliased(Register_login)
    try:
        barang = db.session.query(
            Barang.id,              
            Donatur.name,          
            Barang.nama_barang,     
            Barang.gambar_barang,   
            Barang.tanggal_masuk,
            Donasi.status         
        ).outerjoin(Donasi, Barang.id == Donasi.id_barang 
        ).join(Donatur, Barang.id_donatur == Donatur.id).all()

        detail_barang = [
            {
                "id": a[0],                    
                "donaturName": a[1],           
                "barangName": a[2],            
                "gambar": f"http://localhost:5000/barang/api/get/uploads/{a[3]}" if a[3] else None,  # gambar_barang (DIPERBAIKI)
                "tanggal_masuk": a[4],
                "status": a[5]      
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
        return jsonify({"message": "item berhasil dihapus"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
