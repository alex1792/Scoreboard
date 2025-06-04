# centralized manage SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager

# make it globally available, so other code can use it, and will avoid circular import
db = SQLAlchemy()
login_manager = LoginManager()

# used for broadcasting updated scores
socketio = SocketIO()

# JWT
jwt = JWTManager()
