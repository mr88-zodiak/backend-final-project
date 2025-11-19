from .penerima import penerima
from .barang import barang
from .donasi import donasi
from .klasifikasi import klasifikasi
from .notif import notif


def init_routes(app):
    # app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(penerima, url_prefix='/penerima')
    # app.register_blueprint(donatur , url_prefix='/donatur')
    app.register_blueprint(barang, url_prefix='/barang')
    app.register_blueprint(donasi, url_prefix='/donasi')
    app.register_blueprint(klasifikasi, url_prefix='/klasifikasi')
    app.register_blueprint(notif, url_prefix='/notif')