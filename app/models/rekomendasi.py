from app import db

class HasilRekomendasi(db.Model):
    __tablename__ = "hasil_rekomendasi"
    id = db.Column(db.Integer, primary_key=True)

    id_penerima = db.Column(
        db.Integer,
        db.ForeignKey('register_login.id', ondelete="CASCADE"),
        nullable=False
    )
    id_data_diri_penerima = db.Column(
        db.Integer,
        db.ForeignKey('data_diri_penerima.id', ondelete="CASCADE"),
        nullable=False
    )

    penerima = db.relationship(
        'Register_login',
        backref=db.backref('hasil_rekomendasi', cascade="all, delete-orphan", passive_deletes=True)
    )
    data_diri_penerima = db.relationship(
        'DataDiriPenerima',
        backref=db.backref('hasil_rekomendasi', cascade="all, delete-orphan", passive_deletes=True)
    )

    skor = db.Column(db.Float, nullable=True, default=0.0)

    def __init__(self, id_penerima, id_data_diri_penerima, skor=0.0):
        self.id_penerima = id_penerima
        self.id_data_diri_penerima = id_data_diri_penerima
        self.skor = skor

    def to_dict(self):
        return {
            "id": self.id,
            "id_penerima": self.id_penerima,
            "id_data_diri_penerima": self.id_data_diri_penerima,
            "skor": self.skor
        }
