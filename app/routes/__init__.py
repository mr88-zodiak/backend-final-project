from .user import user
from .barang import barang
from .donasi import donasi
from .klasifikasi import klasifikasi
from .notif import notif
from .pengajuan import pengajuan


def init_routes(app):
    app.register_blueprint(user, url_prefix='/user')
    app.register_blueprint(barang, url_prefix='/barang')
    app.register_blueprint(donasi, url_prefix='/donasi')
    app.register_blueprint(klasifikasi, url_prefix='/klasifikasi')
    app.register_blueprint(notif, url_prefix='/notif')
    app.register_blueprint(pengajuan, url_prefix='/pengajuan')