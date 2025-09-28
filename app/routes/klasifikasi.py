from flask import  jsonify, Blueprint
from app.models.user import *
from app.models.klasifikasi import *
from app.extends import db
import pandas as pd
from sqlalchemy.orm import aliased
import joblib
from flask_jwt_extended import jwt_required

klasifikasi = Blueprint('klasifikasi', __name__)
model = joblib.load('./klasifikasi_model.pkl')
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
            DataDiriPenerima.jenis_kebutuhan,
            HasilKlasifikasi.layak
        ).join(
            HasilKlasifikasi, HasilKlasifikasi.id_penerima == Penerima.id
        ).join(
            DataDiriPenerima, DataDiriPenerima.id_penerima == Penerima.id
        ).all()

        data_list = [
            {
                "id": r[0],
                "name": r[1],
                "penghasilan_perbulan": r[2],
                "jumlah_tanggungan": r[3],
                "jumlah_kendaraan": r[4],
                "status_tempat_tinggal": r[5],
                "jenis_kebutuhan": r[6],
                "layak": r[7]
            } for r in rekomendasi
        ]

        df = pd.DataFrame(data_list)

        df.rename(columns={
            "penghasilan_perbulan": "penghasilan perbulan",
            "jumlah_tanggungan": "jumlah tanggungan",
            "jumlah_kendaraan": "jumlah kendaraan",
            "status_tempat_tinggal": "status tempat tinggal",
            "jenis_kebutuhan": "jenis kebutuhan"
        }, inplace=True)

        features = ["penghasilan perbulan", "jumlah tanggungan", "jumlah kendaraan", "status tempat tinggal", "jenis kebutuhan"]
        predictions = model.predict(df[features])

        for i, row in enumerate(data_list):
            db.session.query(HasilKlasifikasi).filter_by(id_penerima=row["id"]).update({
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
        data = db.session.query(DataDiriPenerima).all()
        return jsonify({
            "data": [d.to_dict() for d in data]
        })
    except Exception as e:
        return jsonify({"message": str(e)}), 500

    