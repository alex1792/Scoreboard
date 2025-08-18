# centralized manage SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager

# make it globally available, so other code can use it, and will avoid circular import
db = SQLAlchemy()
login_manager = LoginManager()

# 修復 SocketIO 配置
socketio = SocketIO(
    cors_allowed_origins="*",  # 允許所有來源，或者指定具體域名
    async_mode='eventlet',
    logger=True,
    engineio_logger=True
)

def init_socketio(app):
    socketio.init_app(app, 
                     cors_allowed_origins="*",
                     async_mode='eventlet')

# JWT
jwt = JWTManager()
