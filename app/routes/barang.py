from flask import request, jsonify
from app.models.user import *
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
@jwt_required()
def get_barang():
    Donatur = aliased(Register_login)
    try:
        barang = db.session.query(
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
                "donaturName": a[1],           
                "barangName": a[2], 
                "kondisi_barang": a[3],           
                "gambar": f"http://localhost:5000/barang/api/get/uploads/{a[4]}" if a[4] else None,
                "tanggal_masuk": a[5],
                "status": a[6],
                "status_pengiriman": a[7]  
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
        return jsonify({"message": str(e)}), 500


@barang.get('/api/chart/totalDonasiBarang')
def get_total_donasi_per_kategori():
    try:
        results = (
            db.session.query(
                DataDiriPenerima.kategori,
                db.func.date(Donasi.tanggal_donasi).label('tanggal'),
                db.func.count(Donasi.id).label('total')
            )
            .join(Barang, Barang.id == Donasi.id_barang)
            .join(DataDiriPenerima, DataDiriPenerima.id_user == Donasi.id_penerima)
            .filter(Donasi.status == 'approved')
            .group_by(DataDiriPenerima.kategori, db.func.date(Donasi.tanggal_donasi))
            .order_by(db.func.date(Donasi.tanggal_donasi))
            .all()
        )

        data = [
            {
                "kategori": r.kategori,
                "tanggal": r.tanggal.strftime("%Y-%m-%d"),
                "total": r.total
            }
            for r in results
        ]
        return jsonify({"data": data}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    
# @barang.get('/api/piechart/totalDonasiBarang')
# def get_total_donasi():
#     try:
#         results = (
#             db.session.query(
#                 DataDiriPenerima.kategori,
#                 db.func.count(Donasi.id),
#                 Donasi.tanggal_donasi  # pastikan kolom ini ada di model Donasi
#             )
#             .join(Barang, Barang.id == Donasi.id_barang)
#             .join(DataDiriPenerima, DataDiriPenerima.id_user == Donasi.id_penerima)
#             .filter(Donasi.status == 'approved')
#             .group_by(DataDiriPenerima.kategori, Donasi.tanggal_donasi)
#             .order_by(Donasi.tanggal_donasi.asc())
#             .all()
#         )

#         data = [
#             {
#                 "kategori": r[0],
#                 "total": r[1],
#                 "tanggal_donasi": r[2].strftime("%Y-%m-%d") if r[2] else None
#             }
#             for r in results
#         ]

#         return jsonify({"data": data}), 200

#     except Exception as e:
#         print(e)
#         return jsonify({"error": str(e)}), 500
