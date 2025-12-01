from app import db

class HasilRekomendasi(db.Model):
    __tablename__ = "hasil_rekomendasi"
    id = db.Column(db.Integer, primary_key=True)
    id_user= db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="CASCADE"),
        nullable=False
    ) 
    id_data_diri_penerima = db.Column(
        db.Integer,
        db.ForeignKey('data_diri_penerima.id', ondelete="CASCADE"),
        nullable=False
    )

    skor = db.Column(db.Float, nullable=True, default=0.0)

    def __init__(self, id_donatur,id_user, id_data_diri_penerima, skor=0.0):
        self.id_donatur = id_donatur
        self.id_user = id_user
        self.id_data_diri_penerima = id_data_diri_penerima
        self.skor = skor

    def to_dict(self):
        return {
            "id": self.id,
            "id_user": self.id_user,
            "id_data_diri_penerima": self.id_data_diri_penerima,
            "skor": self.skor
        }
