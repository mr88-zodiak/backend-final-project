from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt


socketio = SocketIO(cors_allowed_origins="*")
db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()
bcrypt = Bcrypt()
migrate = Migrate()