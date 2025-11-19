from app import db
from datetime import datetime
from sqlalchemy import Enum


class Register_login(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(Enum('admin', 'donatur', 'penerima', name='role_enum',create_type=False), nullable=False, server_default='admin')
    login_stamp = db.Column(db.DateTime, default=None)
    register_stamp = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(Enum('rejected','approved','pending',name="permission_enum",create_type=False), nullable=False, server_default="pending")
    approved_date = db.Column(db.DateTime)
    rejected_date = db.Column(db.DateTime)

    hasi_rekomendasi = db.relationship(
        'HasilRekomendasi',
        backref='users',
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    notifikasi = db.relationship(
        'Notifikasi',
        backref='users',
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    data_diri = db.relationship(
        'DataDiriPenerima',
        backref='users',
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    barang = db.relationship(
        'Barang',
        backref='users',
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    # 🔹 Relasi eksplisit karena dua foreign key menuju ke users
    donasi_donatur = db.relationship(
        "Donasi",
        foreign_keys="[Donasi.id_donatur]",
        backref="donatur",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    donasi_penerima = db.relationship(
        "Donasi",
        foreign_keys="[Donasi.id_penerima]",
        backref="penerima",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __init__(self, name, email, username, password, role):
        self.name = name
        self.email = email
        self.username = username
        self.password = password
        self.role = role
    
    def get_username(self):
        return self.username

    def to_dict(self):
        return {
            "id": self.id,
            "nama": self.name,
            "email": self.email,
            "username": self.username,
            "password": self.password,
            "role": self.role,
            "status": self.status,
            "login_stamp": self.login_stamp,
            "register": self.register_stamp,
            "approve": self.approved_date,
            "rejected": self.rejected_date
        }
class DataDiriPenerima(db.Model):
    __tablename__ = "data_diri_penerima"
    id = db.Column(db.Integer, primary_key=True)
    penghasilan_perbulan = db.Column(db.Integer, nullable=False)
    jumlah_tanggungan = db.Column(db.Integer, nullable=False)
    status_tempat_tinggal = db.Column(db.String(100), nullable=False)
    jumlah_kendaraan = db.Column(db.Integer, nullable=False)
    kategori = db.Column(Enum('buku','pakaian','furniture','elektronik','peralatan dapur',name="kategori_enum",create_type=False), nullable=False,server_default="buku")
    jumlah = db.Column(db.Integer, nullable=False)
    jenis_kebutuhan = db.Column(db.String(100), nullable=False)
    alamat = db.Column(db.String(100), nullable=True)
    id_user = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    hasil_rekomendasi = db.relationship(
        "HasilRekomendasi",
        backref="data_diri_penerima",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    hasil_klasifikasi = db.relationship(
        "HasilKlasifikasi",
        backref="data_diri_penerima",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __init__(self, id_user, penghasilan_perbulan, jumlah_tanggungan, status_tempat_tinggal, jumlah_kendaraan,kategori, jenis_kebutuhan,jumlah):
        self.id_user = id_user
        self.penghasilan_perbulan = penghasilan_perbulan
        self.jumlah_tanggungan = jumlah_tanggungan
        self.status_tempat_tinggal = status_tempat_tinggal
        self.jumlah_kendaraan = jumlah_kendaraan
        self.jenis_kebutuhan = jenis_kebutuhan
        self.jumlah = jumlah
        self.kategori = kategori
        # self.alamat = alamat

    def to_dict(self):
        return {
            "id": self.id,
            "penghasilan_perbulan": self.penghasilan_perbulan,
            "jumlah_tanggungan": self.jumlah_tanggungan,
            "status_tempat_tinggal": self.status_tempat_tinggal,
            "jumlah_kendaraan": self.jumlah_kendaraan,
            "kategori": self.kategori,
            "jenis_kebutuhan": self.jenis_kebutuhan,
            "id_user": self.id_user
        }

class Donasi(db.Model):
    __tablename__ = "donasi"
    id = db.Column(db.Integer, primary_key=True)
    id_donatur = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    id_penerima = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    id_barang = db.Column(db.Integer, db.ForeignKey("barang.id", ondelete="CASCADE"), nullable=True)
    tanggal_donasi = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(100), nullable=True, default="pending")
    status_pengiriman = db.Column(db.Enum('pick_up', 'delivered','delivering','cancelled','done','rejected', name="metode_enum",create_type=False), nullable=True, default='pick_up')
    # status_donasi = db.Column(db.Enum('menunggu_penjemputan', 'dalam_perjalanan', 'tersalurkan', name="status_enum"), default='menunggu_penjemputan')
    tanggal_approve = db.Column(db.DateTime, nullable=True)
    tanggal_reject = db.Column(db.DateTime, nullable=True)

    donasi_notifikasi = db.relationship(
        'Notifikasi',
        backref='donasi',
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __init__(self, id_donatur, id_penerima, id_barang, tanggal_donasi):
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
            "status_pengiriman" : self.status_pengiriman,
            "tanggal_donasi": self.tanggal_donasi,
            "status": self.status,
            "tanggal_approve": self.tanggal_approve,
        }
class Barang(db.Model):
    __tablename__ = "barang"
    id = db.Column(db.Integer, primary_key=True)
    id_donatur = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="CASCADE"),
        nullable=True
    )
    nama_barang = db.Column(db.String(100), nullable=False)
    kondisi_barang = db.Column( db.Integer, nullable=False, server_default='1')
    gambar_barang = db.Column(db.String(255), nullable=True)
    tanggal_masuk = db.Column(db.DateTime, nullable=True)

    # Relasi ke donasi
    donasi = db.relationship(
        'Donasi',
        backref='barang',
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    notifikasi = db.relationship(
        'Notifikasi',
        backref='barang',
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __init__(self, nama_barang, gambar_barang, id_donatur, tanggal_masuk,kondisi_barang=1):
        self.id_donatur = id_donatur
        self.nama_barang = nama_barang
        self.kondisi_barang = kondisi_barang
        self.gambar_barang = gambar_barang
        self.tanggal_masuk = tanggal_masuk

    def to_dict(self):
        return {
            "id": self.id,
            "id_donatur": self.id_donatur,
            "nama_barang": self.nama_barang,
            "gambar_barang": self.gambar_barang,
            "tanggal_masuk": self.tanggal_masuk
        }
# class DonasiNew(db.Model):
#     __tablename__ = 'donasinew'
#     id = db.Column(db.Integer, primary_key=True)
#     penerima_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
#     barang_id = db.Column(db.Integer, db.ForeignKey("barang.id", ondelete="CASCADE"), nullable=True)
#     donasi_id = db.Column(db.Integer, db.ForeignKey('donasi.id', ondelete="CASCADE"), nullable=True)
#     personal_id = db.Column(db.Integer, db.ForeignKey('data_diri_penerima.id'), nullable=True)

#     def __init__(self, penerima_id, barang_id, donasi_id, personal_id):
#         self.penerima_id = penerima_id
#         self.barang_id = barang_id
#         self.donasi_id = donasi_id
#         self.personal_id = personal_id

#     donasi = db.relationship(
#         ''
#     )

