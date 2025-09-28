from app import db
from datetime import datetime
from sqlalchemy import Enum


class Register_login(db.Model):
    __tablename__ = "register_login"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(Enum('admin', 'donatur', 'penerima',name='role_enum'), nullable=False , default='admin')
    login_stamp = db.Column(db.DateTime, default=None)
    register_stamp = db.Column(db.DateTime, default=datetime.now)

    # Relasi ke data diri
    data_diri = db.relationship(
        'DataDiriPenerima',
        backref='register_login',
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    hasil_klasifikasi = db.relationship(
        "HasilKlasifikasi",
        backref="register_login",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    # Relasi ke donasi
    donasi = db.relationship(
        'Donasi',
        backref='register_login',
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    barang = db.relationship(
        'Barang',
        backref='register_login',
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __init__(self, name, email, username, password,role):
        self.name = name
        self.email = email
        self.username = username
        self.password = password
        self.role = role

    def to_dict(self):
        return {
            "id": self.id,
            "nama": self.name,
            "email": self.email,
            "username": self.username,
            "password": self.password,
            "login_stamp": self.login_stamp,
            "register": self.register_stamp
        }


# class Donatur(db.Model):
#     __tablename__ = "donatur"
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     password = db.Column(db.String(200), nullable=False)
#     login_stamp = db.Column(db.DateTime, nullable=True)
#     register_stamp = db.Column(db.DateTime, default=datetime.now)
#     pasif_delete = db.Column(db.Boolean, default=False)

#     # Relasi ke barang
#     barang = db.relationship(
#         'Barang',
#         backref='donatur',
#         cascade="all, delete-orphan",
#         passive_deletes=True
#     )

#     # Relasi ke donasi
#     donasi = db.relationship(
#         'Donasi',
#         backref='donatur',
#         cascade="all, delete-orphan",
#         passive_deletes=True
#     )

#     def __init__(self, name, email, username, password, login_stamp=None):
#         self.name = name
#         self.email = email
#         self.username = username
#         self.password = password
#         self.login_stamp = login_stamp

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "name": self.name,
#             "email": self.email,
#             "username": self.username,
#             "password": self.password,
#             "login_stamp": self.login_stamp,
#             "register": self.register_stamp
#         }


# class Admin(db.Model):
#     __tablename__ = "admin"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     password = db.Column(db.String(200), nullable=False)
#     login_stamp = db.Column(db.DateTime, default=datetime.now)

#     def __init__(self, username, password):
#         self.username = username
#         self.password = password

#     def to_dict(self):
#         return {"id": self.id, "username": self.username}


class DataDiriPenerima(db.Model):
    __tablename__ = "data_diri_penerima"
    id = db.Column(db.Integer, primary_key=True)
    penghasilan_perbulan = db.Column(db.Integer, nullable=False)
    jumlah_tanggungan = db.Column(db.Integer, nullable=False)
    status_tempat_tinggal = db.Column(db.String(100), nullable=False)
    jumlah_kendaraan = db.Column(db.Integer, nullable=False)
    jenis_kebutuhan = db.Column(db.String(100), nullable=False)

    id_penerima = db.Column(
        db.Integer,
        db.ForeignKey('register_login.id', ondelete="CASCADE"),
        nullable=False
    )

    def __init__(self, id_penerima, penghasilan_perbulan, jumlah_tanggungan, status_tempat_tinggal, jumlah_kendaraan, jenis_kebutuhan):
        self.id_penerima = id_penerima
        self.penghasilan_perbulan = penghasilan_perbulan
        self.jumlah_tanggungan = jumlah_tanggungan
        self.status_tempat_tinggal = status_tempat_tinggal
        self.jumlah_kendaraan = jumlah_kendaraan
        self.jenis_kebutuhan = jenis_kebutuhan

    def to_dict(self):
        return {
            "id": self.id,
            "penghasilan_perbulan": self.penghasilan_perbulan,
            "jumlah_tanggungan": self.jumlah_tanggungan,
            "status_tempat_tinggal": self.status_tempat_tinggal,
            "jumlah_kendaraan": self.jumlah_kendaraan,
            "jenis_kebutuhan": self.jenis_kebutuhan,
            "id_penerima": self.id_penerima
        }


class Donasi(db.Model):
    __tablename__ = "donasi"
    id = db.Column(db.Integer, primary_key=True)

    id_donatur = db.Column(
        db.Integer,
        db.ForeignKey('register_login.id', ondelete="CASCADE"),
        nullable=False
    )
    id_penerima = db.Column(
        db.Integer,
        db.ForeignKey('register_login.id', ondelete="CASCADE"),
        nullable=False
    )
    id_barang = db.Column(
        db.Integer,
        db.ForeignKey('barang.id', ondelete="CASCADE"),
        nullable=True
    )

    tanggal_donasi = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(100), nullable=True, default="pending")
    tanggal_approve = db.Column(db.DateTime, nullable=True)

    def __init__(self, id_barang, id_donatur, id_penerima, tanggal_donasi):
        self.id_donatur = id_donatur
        self.id_penerima = id_penerima
        self.id_barang = id_barang
        self.tanggal_donasi = tanggal_donasi

    def to_dict(self):
        return {
            "id": self.id,
            "id_donatur": self.id_donatur,
            "id_penerima": self.id_penerima,
            "id_barang": self.id_barang,
            "tanggal_donasi": self.tanggal_donasi,
            "status": self.status,
            "tanggal_approve": self.tanggal_approve,
        }


class Barang(db.Model):
    __tablename__ = "barang"
    id = db.Column(db.Integer, primary_key=True)

    id_donatur = db.Column(
        db.Integer,
        db.ForeignKey('register_login.id', ondelete="CASCADE"),
        nullable=True
    )

    nama_barang = db.Column(db.String(100), nullable=False)
    gambar_barang = db.Column(db.String(255), nullable=True)
    tanggal_masuk = db.Column(db.DateTime, nullable=True)

    # Relasi ke donasi
    donasi = db.relationship(
        'Donasi',
        backref='barang',
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __init__(self, nama_barang, gambar_barang, id_donatur, tanggal_masuk):
        self.id_donatur = id_donatur
        self.nama_barang = nama_barang
        self.gambar_barang = gambar_barang
        self.tanggal_masuk = tanggal_masuk

    def to_dict(self):
        return {
            "id": self.id,
            "nama_barang": self.nama_barang,
            "gambar_barang": self.gambar_barang,
            "tanggal_masuk": self.tanggal_masuk
        }
