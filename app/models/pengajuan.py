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
    jenis_barang = db.Column(db.String(100), nullable=False)
    nama_barang = db.Column(db.String(100), nullable=False)
    approve = db.Column(db.Boolean, default=False)
    tanggal_approve = db.Column(db.DateTime)
    tanggal_reject = db.Column(db.DateTime)
    tanggal_pengajuan = db.Column(db.DateTime, default=datetime.now)
    pesan_reject = db.Column(db.String(255), nullable=True) 

    def __init__(self, id_penerima, jenis_barang, nama_barang):
        self.id_penerima = id_penerima
        self.jenis_barang = jenis_barang
        self.nama_barang = nama_barang

    def to_dict(self):
        return{
            'id_penerima': self.id_penerima,
            'jenis_barant': self.jenis_barang,
            'nama_barang': self.nama_barang,
            'approve': self.approve,
            'tanggal_approve': self.tanggal_approve,
            'tanggal_reject': self.tanggal_reject,
            'tanggal_pengajuan': self.tanggal_pengajuan,
            'pesan_reject': self.pesan_reject
        }


    
    