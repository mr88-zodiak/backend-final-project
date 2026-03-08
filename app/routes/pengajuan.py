from flask import Blueprint
from app.models.user import *
from app.models.pengajuan import *
from flask import request, jsonify,send_from_directory,current_app
from datetime import datetime
from config import Config
from werkzeug.utils import secure_filename
import os
from PIL import Image
from app.extends import socketio
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity


pengajuan = Blueprint('pengajuan', __name__)
nama_barangBannned = [
  'mobil bekas',
  'mobil',
  'motor bekas',
  'motor',
  'sepeda motor',
  'sepeda',
  'tank',
  'mobil tank',
  'senjata api',
  'senjata',
  'bensin',
  'narkoba',
  'obat terlarang',
  'bahan peledak',
  'bom',
  'pesawat tempur',
  'pesawat',
  'kapal perang',
  'kapal selam',
  'alat perang',
  'helikopter tempur',
  'helikopter',
  'granat',
  'peluru',
  'amunisi',
  'tai',
  'kotoran',
  'bangkai',
  'mayat',
  'babi',
  'kambing',
  'sapi',
  'ayam',
  'ikan'
]
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# def uploaded_file(filename):
#     return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
# def compress_image(
#     input_path,
#     output_path,
#     max_size=(1024, 1024),
#     quality=75
# ):
#     img = Image.open(input_path)
#     img.thumbnail(max_size)

#     ext = os.path.splitext(output_path)[1].lower()

#     if ext in ['.jpg', '.jpeg']:
#         img = img.convert("RGB")
#         img.save(output_path, quality=quality, optimize=True)

#     elif ext == '.png':
#         img.save(output_path, optimize=True)

#     elif ext == '.webp':
#         img.save(output_path, format='WEBP', quality=quality, method=6)
#     else:
#         raise ValueError("Format tidak didukung")

@pengajuan.post('/api/post/pengajuan_barang')
@jwt_required()
def pengajuanBarangNw():
    id_user = get_jwt_identity()

    try:
        data = request.get_json()
        name_barang = data.get('nama_barang')
        jenis_barang = data.get('jenis_barang')
        jumlah = data.get('jumlah')
        print(f"===DEBUG===\n[+] name_barang: {name_barang}\n[+] jenis_barang: {jenis_barang}\n [+] jumlah: {jumlah} ")
        if name_barang is None:
            return jsonify({"error": "Nama barang wajib diisi"}), 400
        if jenis_barang is None:
            return jsonify({"error": "Jenis barang wajib diisi"}), 400
        if jumlah is None:
            return jsonify({"error": "Jumlah barang wajib diisi"}), 400
        if name_barang.lower() in nama_barangBannned:
            return jsonify({"error": "Nama barang tidak diperbolehkan"}), 400
        
        

        form_pengajuan = pengajuanBarang(
            id_penerima=id_user,
            nama_barang=name_barang,
            jenis_barang=jenis_barang
            ,jumlah=jumlah
        )

        db.session.add(form_pengajuan)
        db.session.commit()
        socketio.emit('data_update',  {'message': 'Donasi diperbarui'})
        return jsonify({'message': 'Pengajuan barang berhasil'}), 201

    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({
            'message': 'Gagal mengajukan barang',
            'error': str(e)
        }), 500

@pengajuan.delete("/api/delete/pengajuan_barang/<int:id>")
@jwt_required()
def deletePengajuanBarang(id):
    try:
        pengajuan = pengajuanBarang.query.get(id)
        if not pengajuan:
            return jsonify({'message': 'Pengajuan barang tidak ditemukan'}), 404

        db.session.delete(pengajuan)
        db.session.commit()
        socketio.emit('data_update',  {'message': 'Donasi diperbarui'})
        return jsonify({'message': 'Pengajuan barang berhasil dihapus'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Gagal menghapus pengajuan barang',
            'error': str(e)
        }), 500
@pengajuan.put("/api/put/approve/pengajuan_barang/<int:id>")
@jwt_required()
def pengajuanApproved(id):
    try:
        pengajuan = pengajuanBarang.query.get(id)
        if not pengajuan:
            return jsonify({'message': 'Pengajuan barang tidak ditemukan'}), 404
        pengajuan.status = 'approved'
        pengajuan.tanggal_approve = datetime.now()
        db.session.commit()
        socketio.emit('data_update',  {'message': 'Donasi diperbarui'})
        return jsonify({'message': 'Pengajuan barang disetujui'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Gagal menyetujui pengajuan barang', 'error': str(e)}), 500

@pengajuan.put("/api/put/reject/pengajuan_barang/<int:id>")
@jwt_required()
def pengajuanReject(id):
    try:
        pengajuan = pengajuanBarang.query.get(id)
        if not pengajuan:
            return jsonify({'message': 'Pengajuan barang tidak ditemukan'}), 404
        pengajuan.approve = 'rejected'
        pengajuan.tanggal_reject = datetime.now()
        db.session.commit()
        return jsonify({'message': 'Pengajuan barang ditolak'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Gagal menolak pengajuan barang', 'error': str(e)}), 500
@pengajuan.post('/api/post/pesan_reject/<int:id>')
@jwt_required()
def postPesanReject():
    try:
        pesan_reject = request.json.get('pesan_reject')

        pengajuan = pengajuanBarang.query.get(id)
        if not pengajuan:
            return jsonify({'message': 'Pengajuan barang tidak ditemukan'}), 404

        pengajuan.pesan_reject = pesan_reject
        db.session.commit()
        socketio.emit('data_update',  {'message': 'Donasi diperbarui'})
        return jsonify({'message': 'Pesan reject berhasil ditambahkan'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Gagal menambahkan pesan reject', 'error': str(e)}), 500
@pengajuan.get("/api/get/pengajuan_barang")
@jwt_required()
def getPengajuanBarang():
    try:
        pengajuan_list = (
            db.session.query(
                pengajuanBarang.id.label("id"),
                pengajuanBarang.id_penerima.label("id_penerima"),
                Register_login.name.label("nama_penerima"),
                pengajuanBarang.nama_barang.label("nama_barang"),
                pengajuanBarang.jenis_barang.label("jenis_barang"),
                pengajuanBarang.jumlah.label("jumlah"),
                pengajuanBarang.status.label("status"),
                pengajuanBarang.tanggal_approve.label("tanggal_approve"),
                pengajuanBarang.tanggal_reject.label("tanggal_reject"),
                pengajuanBarang.tanggal_pengajuan.label("tanggal_pengajuan"),
                pengajuanBarang.pesan_reject.label("pesan_reject"),
            )
            .join(Register_login, Register_login.id == pengajuanBarang.id_penerima)
            .filter(pengajuanBarang.id_penerima == get_jwt_identity())
            .order_by(pengajuanBarang.id.asc())
            .all()
        )

        detail_pengajuan = [
            {
                "id": p.id,
                "id_penerima": p.id_penerima,
                "nama_penerima": p.nama_penerima,
                "nama_barang": p.nama_barang,
                "jenis_barang": p.jenis_barang,
                "jumlah": p.jumlah,
                "status": p.status,
                "tanggal_approve": p.tanggal_approve,
                "tanggal_reject": p.tanggal_reject,
                "tanggal_pengajuan": p.tanggal_pengajuan,
                "pesan_reject": p.pesan_reject,
            }
            for p in pengajuan_list
        ]

        return jsonify({"data": detail_pengajuan}), 200

    except Exception as e:
        return jsonify({
            "message": "Gagal mengambil data pengajuan barang",
            "error": str(e)
        }), 500

@pengajuan.get("/api/get/pengajuanB")
@jwt_required()
def getPengajuanBarangB():
    try:
        pengajuan_list = (
            db.session.query(
                pengajuanBarang.id.label("id"),
                pengajuanBarang.id_penerima.label("id_penerima"),
                Register_login.name.label("nama_penerima"),
                pengajuanBarang.nama_barang.label("nama_barang"),
                pengajuanBarang.jenis_barang.label("jenis_barang"),
                pengajuanBarang.jumlah.label("jumlah"),
                pengajuanBarang.status.label("status"),
                pengajuanBarang.tanggal_approve.label("tanggal_approve"),
                pengajuanBarang.tanggal_reject.label("tanggal_reject"),
                pengajuanBarang.tanggal_pengajuan.label("tanggal_pengajuan"),
                pengajuanBarang.pesan_reject.label("pesan_reject"),
            )
            .outerjoin(Register_login, Register_login.id == pengajuanBarang.id_penerima)
            .filter(Register_login.role == 'penerima')
            .order_by(Register_login.id.asc())
            .all()
        )

        detail_pengajuan = [
            {
                "id": p.id,
                "id_penerima": p.id_penerima,
                "nama_penerima": p.nama_penerima,
                "nama_barang": p.nama_barang,
                "jenis_barang": p.jenis_barang,
                "jumlah": p.jumlah,
                "status": p.status,
                "tanggal_approve": p.tanggal_approve,
                "tanggal_reject": p.tanggal_reject,
                "tanggal_pengajuan": p.tanggal_pengajuan,
                "pesan_reject": p.pesan_reject,
            }
            for p in pengajuan_list
        ]

        return jsonify({"data": detail_pengajuan}), 200

    except Exception as e:
        return jsonify({
            "message": "Gagal mengambil data pengajuan barang",
            "error": str(e)
        }), 500

@pengajuan.patch("/api/patch/pengajuan_barang/<int:id>")
@jwt_required()
def updatePengajuanBarang(id):
    try:
        pengajuan = pengajuanBarang.query.get(id)

        if not pengajuan:
            return jsonify({'message': 'Pengajuan barang tidak ditemukan'}), 404

        data = request.get_json()
        nama_barang = data.get("nama_barang")
        jenis_barang = data.get("jenis_barang")
        jumlah = data.get("jumlah")

        if not data:
            return jsonify({'message': 'Tidak ada data untuk diperbarui'}), 400

        if nama_barang and nama_barang.strip() != '':
            pengajuan.nama_barang = nama_barang

        if jenis_barang and jenis_barang.strip() != '':
            pengajuan.jenis_barang = jenis_barang
        
        if jumlah is not None:
            pengajuan.jumlah = jumlah

        db.session.commit()

        socketio.emit(
            'data_update',
            {
                'id': pengajuan.id,
                'nama_barang': pengajuan.nama_barang,
                'jenis_barang': pengajuan.jenis_barang,
                'jumlah': pengajuan.jumlah
            }
        )

        return jsonify({'message': 'Pengajuan barang berhasil diperbarui'}), 200

    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({
            'message': 'Gagal memperbarui pengajuan barang',
            'error': str(e)
        }), 500

