from asyncio.log import logger
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_socketio import SocketIO
from flask_cors import CORS

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
cache = Cache()
socketio = SocketIO(cors_allowed_origins="*")
cors = CORS()
