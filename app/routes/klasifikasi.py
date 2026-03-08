from flask import  jsonify, Blueprint
from sqlalchemy import func
from app.models.user import *
from app.models.klasifikasi import *
from app.models.pengajuan import *
from app.extends import db
import pandas as pd
from sqlalchemy.orm import aliased
import joblib
from flask_jwt_extended import jwt_required

klasifikasi = Blueprint('klasifikasi', __name__)
@klasifikasi.get("/api/get/data")
@jwt_required()
def get_rekomendasi():
    Penerima = aliased(Register_login)
    try:
        rekomendasi = db.session.query(
        Penerima.id,
        Penerima.name,
        DataDiriPenerima.penghasilan_perbulan,
        DataDiriPenerima.jumlah_tanggungan,
        DataDiriPenerima.jumlah_kendaraan,
        DataDiriPenerima.status_tempat_tinggal,
        pengajuanBarang.nama_barang.label("nama_barang"),
        pengajuanBarang.jumlah.label("jumlah_barang"),
        HasilKlasifikasi.layak
    ).outerjoin(
        HasilKlasifikasi, HasilKlasifikasi.id_user == Penerima.id
    ).outerjoin(
        DataDiriPenerima, DataDiriPenerima.id_user == Penerima.id
    ).outerjoin(
        pengajuanBarang, pengajuanBarang.id_penerima == Penerima.id
    ).filter(
    DataDiriPenerima.penghasilan_perbulan != None,
    DataDiriPenerima.jumlah_tanggungan != None,
    DataDiriPenerima.jumlah_kendaraan != None,
    DataDiriPenerima.status_tempat_tinggal != None
).order_by(Penerima.id.asc()).all()


        data_list = [
        {
            "id": r[0],
            "name": r[1],
            "penghasilan_perbulan": r[2],
            "jumlah_tanggungan": r[3],
            "jumlah_kendaraan": r[4],
            "status_tempat_tinggal": r[5],
            "nama_barang": r[6],
            "jumlah_barang": r[7],
            "layak": r[8]                  
        } for r in rekomendasi
        ]


        df = pd.DataFrame(data_list)
        df.rename(columns={
            "penghasilan_perbulan": "penghasilan perbulan",
            "jumlah_tanggungan": "jumlah tanggungan",
            "jumlah_kendaraan": "jumlah kendaraan",
            "status_tempat_tinggal": "status tempat tinggal"
        }, inplace=True)
        # fitur_model = [
        #     "penghasilan perbulan",
        #     "jumlah tanggungan",
        #     "jumlah kendaraan",
        #     "status tempat tinggal"
        # ]
        print("====== DEBUG DF ======")
        print(df)
        print("COLUMNS:", df.columns.tolist())
        print("DTYPES:", df.dtypes)

        predictions = HasilKlasifikasi.klasifikasi_predict(df)
        for i, row in enumerate(data_list):
            db.session.query(HasilKlasifikasi).filter_by(id_user=row["id"]).update({
                "layak": int(predictions[i])
            })

        db.session.commit()

        return jsonify({"data" : data_list}), 200

    except Exception as e:
        print("Error:", e)
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@klasifikasi.get("/api/get/data/getData")
@jwt_required()
def getData():
    try:
        data = (
            db.session.query(
            Register_login.id,
            Register_login.name,
            pengajuanBarang.jenis_barang,
            pengajuanBarang.nama_barang,
            Register_login.status,
            pengajuanBarang.jumlah,
            HasilKlasifikasi.layak,
            func.sum(Donasi.donasi_terkumpul).label("donasi_total")
        )
        .outerjoin(pengajuanBarang, pengajuanBarang.id_penerima == Register_login.id)
        .outerjoin(HasilKlasifikasi, HasilKlasifikasi.id_user == Register_login.id)
        .outerjoin(Donasi, Donasi.id_penerima == Register_login.id)
        .group_by(
            Register_login.id,
            pengajuanBarang.id,
            HasilKlasifikasi.layak
        )
        .all()

            # .outerjoin(pengajuanBarang, pengajuanBarang.id_penerima == Register_login.id)
            # .outerjoin(Donasi, Donasi.id_barang == pengajuanBarang.id)
            # .outerjoin(HasilKlasifikasi, HasilKlasifikasi.id_data_diri == pengajuanBarang.id)
        )

        data_list = [
            {
                "id": d[0],
                "name": d[1],
                "kategori": d[2],
                "jenis_kebutuhan": d[3],
                "status": d[4],
                "jumlah": d[5],
                "layak": d[6],
                "donasi_terkumpul": d[7]
            }
            for d in data
        ]

        return jsonify({"data": data_list}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500


    