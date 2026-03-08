from app import db
from datetime import datetime


class pengajuanBarang(db.Model):
    __tablename__ = "pengajuan_barang"
    id = db.Column(db.Integer, primary_key=True)
    id_penerima = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete= "CASCADE"),
        nullable=False
    )
    nama_barang = db.Column(db.String(100), nullable=False)
    jenis_barang = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(50), nullable=True, default="pending")
    jumlah = db.Column(db.Integer, nullable=True)
    tanggal_approve = db.Column(db.DateTime)
    tanggal_reject = db.Column(db.DateTime)
    tanggal_pengajuan = db.Column(db.DateTime, default=datetime.now)
    pesan_reject = db.Column(db.String(255), nullable=True) 

    def __init__(self, id_penerima, nama_barang,jenis_barang,jumlah):
        self.id_penerima = id_penerima
        self.nama_barang = nama_barang
        self.jenis_barang = jenis_barang
        self.jumlah = jumlah

    def to_dict(self):
        return{
            'id_penerima': self.id_penerima,
            'nama_barang': self.nama_barang,
            'jenis_barang': self.jenis_barang,
            'jumlah': self.jumlah,
            'status': self.status,
            'tanggal_approve': self.tanggal_approve,
            'tanggal_reject': self.tanggal_reject,
            'tanggal_pengajuan': self.tanggal_pengajuan,
            'pesan_reject': self.pesan_reject
        }


    
    