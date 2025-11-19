from app import db
from datetime import datetime

class Notifikasi(db.Model):
    __tablename__ = "notifikasi"
    id = db.Column(db.Integer, primary_key=True)
    id_donatur = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="CASCADE"),
        nullable=True
    )
    id_barang = db.Column(
        db.Integer,
        db.ForeignKey('barang.id', ondelete="CASCADE"),
        nullable=False
    )
    id_donasi = db.Column(
        db.Integer,
        db.ForeignKey('donasi.id', ondelete="CASCADE"),
        nullable=True
    )
    pesan = db.Column(db.String(255), nullable=False)
    tanggal = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, id_barang,id_donasi,id_donatur ,pesan):
        self.id_barang = id_barang   
        self.id_donasi = id_donasi
        self.id_donatur = id_donatur
        self.pesan = pesan

    def to_dict(self):
        return {
            "id": self.id,
            "id_barang": self.id_barang, 
            "pesan": self.pesan,
            "tanggal": self.tanggal.isoformat() if self.tanggal else None,
        }
