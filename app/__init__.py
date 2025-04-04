import sqlite3
from flask import Flask
from config import Config
from flask_login import LoginManager, current_user
from .db import Database, User
from .routes import home_blueprint, scoreboard_blueprint, umpire_blueprint
from .extensions import socketio
# from flask_socketio import SocketIO

# socketio = SocketIO()   #   used for broadcasting scoore

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config.from_mapping(SECRET_KEY='dev')

    # used for broadcasting scoore
    # socketio.init_app(app, cors_allowed_origins="*")
    # socketio.init_app(app)

    # initialize login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # define user_loader function
    @login_manager.user_loader
    def load_user(user_id):
        try:
            conn = sqlite3.connect('database.db', timeout=10.0)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user_info = cursor.fetchone()
            if user_info:
                return User(user_info[0], user_info[1], user_info[2])
            else:
                return None
        except sqlite3.OperationalError as e:
            print(f"Error loading user: {e}")
            return None
        finally:
            conn.close()

    # register blueprints
    app.register_blueprint(home_blueprint)
    app.register_blueprint(scoreboard_blueprint)
    app.register_blueprint(umpire_blueprint)
    from . import auth
    app.register_blueprint(auth.bp)
    
    # initialize database
    with app.app_context():
        db_name = 'database.db'
        db = Database(db_name)
        db.close()

    # initialize SocketIO
    socketio.init_app(app, 
        cors_allowed_origins="*",
        logger=True,
        engineio_logger=True,
        async_mode='eventlet'  # make sure its eventlet async_mode
    )
    
    return app