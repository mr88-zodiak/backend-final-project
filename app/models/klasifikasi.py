from app import db
import joblib
import pandas as pd

model = joblib.load('./knn_model_fix.pkl')

class HasilKlasifikasi(db.Model):
    
    __tablename__ = "hasil_klasifikasi"
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    id_data_diri = db.Column(
        db.Integer,
        db.ForeignKey("data_diri_penerima.id", ondelete="CASCADE"),
        nullable=False
    )

    layak = db.Column(db.Integer, nullable=True, default=0)

    @staticmethod
    def klasifikasi_predict(df: pd.DataFrame):
        try:
            features = [
                "penghasilan perbulan",
                "jumlah tanggungan",
                "jumlah kendaraan",
                "status tempat tinggal",
                "jenis kebutuhan"
            ]

            # pastikan semua fitur tersedia
            missing = [f for f in features if f not in df.columns]
            if missing:
                raise ValueError(f"Missing features: {missing}")

            # prediksi menggunakan model
            predictions = model.predict(df[features])
            return predictions.tolist()

        except Exception as e:
            print("Error in klasifikasi_predict:", e)
            raise
    def __init__(self, id_user, id_data_diri):
        self.id_user = id_user
        self.id_data_diri = id_data_diri
