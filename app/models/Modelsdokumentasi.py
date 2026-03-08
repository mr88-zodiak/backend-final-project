from app import db
from datetime import datetime


class Dokumentasi(db.Model):
    __tablename__ = "dokumentasi"
    id = db.Column(db.Integer, primary_key=True)
    id_donatur = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file = db.Column(db.String(255), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    ukuran_file = db.Column(db.String(255), nullable=False)
    tanggal_dokumentasi = db.Column(db.DateTime)

    def __init__(self, file, ukuran_file,file_name,tanggal_dokumentasi,id_donatur):
        self.id_donatur = id_donatur
        self.file = file
        self.file_name = file_name
        self.ukuran_file = ukuran_file
        self.tanggal_dokumentasi = tanggal_dokumentasi

    def to_dict(self):
        return{
            "file" : f"http://localhost:5000/pengajuan/api/get/uploads/{self.file}",
            "file_name" : self.file_name,
            "ukuran_file": self.ukuran_file,
            "tanggal_dokumentasi" : self.tanggal_dokumentasi
        }
    