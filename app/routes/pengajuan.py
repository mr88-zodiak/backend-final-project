from flask import Blueprint
from app.models.user import *
from app.models.pengajuan import *
from flask import request, jsonify
from datetime import datetime
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity


pengajuan = Blueprint('pengajuan', __name__)

@pengajuan.post('/api/post/pengajuan_barang')
@jwt_required()
def pengajuanBarang():
    id_user = get_jwt_identity()
    jenis_barang = request.json.get('jenis_barang')
    nama_barang = request.json.get('nama_barang')
    try:
        if not jenis_barang or not nama_barang:
            return jsonify({'message': 'Jenis barang dan jumlah harus diisi'}), 400
        form_pengajuan = pengajuanBarang(
            id_penerima=id_user,
            jenis_barang= jenis_barang,
            nama_barang= nama_barang
        )
        db.session.add(form_pengajuan)
        db.session.commit()
        return jsonify({'message': 'Pengajuan barang berhasil'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Gagal mengajukan barang', 'error': str(e)}), 500

@pengajuan.put("/api/put/approved/pengajuan_barang/<int:id>")
@jwt_required()
def pengajuanApproved(id):
    try:
        pengajuan = pengajuanBarang.query.get(id)
        if not pengajuan:
            return jsonify({'message': 'Pengajuan barang tidak ditemukan'}), 404
        pengajuan.approve = True
        pengajuan.tanggal_approve = datetime.now()
        db.session.commit()
        if pengajuan.approve == True:
            return jsonify({'status': 'approved'}), 200
        else:
            return jsonify({'status': 'rejected'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Gagal menyetujui pengajuan barang', 'error': str(e)}), 500

@pengajuan.get("/api/get/pengajuan_barang")
@jwt_required()
def getPengajuanBarang():
    try:
        pengajuan_list = db.session.query(Register_login.name, pengajuanBarang.nama_barang, pengajuanBarang.jenis_barang, pengajuanBarang.approve, pengajuanBarang.tanggal_approve, pengajuanBarang.tanggal_reject, pengajuanBarang.tanggal_pengajuan,pengajuanBarang.pesan_reject).join(
            pengajuanBarang, Register_login.id == pengajuanBarang.id_penerima
        ).where(Register_login.role == 'penerima').all()
        data_list = [
            {
                'name': pengajuan.name,
                'nama_barang': pengajuan.nama_barang,
                'jenis_barang': pengajuan.jenis_barang
            }
            for pengajuan in pengajuan_list
        ]
        return jsonify({"data" : data_list}), 200
    except Exception as e:
        return jsonify({'message': 'Gagal mengambil data pengajuan barang', 'error': str(e)}), 500