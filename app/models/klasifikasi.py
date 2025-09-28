from app import db

class HasilKlasifikasi(db.Model):
    __tablename__ = "hasil_klasifikasi"
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
    # penerima = db.relationship('Penerima', backref=db.backref('hasil_klasifikasi', lazy=True))
    penerima = db.relationship(
    'Register_login',
    backref=db.backref('hasil_klasifikasi', cascade="all, delete-orphan", passive_deletes=True))

    data_diri_penerima = db.relationship('DataDiriPenerima', backref=db.backref('hasil_klasifikasi', lazy=True))
    layak = db.Column(db.Integer, nullable=True, default=0)

    def __init__(self, id_penerima, id_data_diri_penerima):
        self.id_penerima = id_penerima
        self.id_data_diri_penerima = id_data_diri_penerima
