import sqlite3
from flask import Flask
from config import Config
from flask_login import LoginManager, current_user
from .db import Database, User
from .routes import (home_blueprint, scoreboard_blueprint, umpire_blueprint, 
                     admin_blueprint, users_blueprint, match_blueprint,
                     manage_match_blueprint, create_match_blueprint, clear_all_match_blueprint)
from .extensions import socketio

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config.from_mapping(SECRET_KEY='dev')


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
                return User(*user_info)
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
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(users_blueprint)
    app.register_blueprint(match_blueprint)
    app.register_blueprint(manage_match_blueprint)
    app.register_blueprint(create_match_blueprint)
    app.register_blueprint(clear_all_match_blueprint)
    from . import auth
    app.register_blueprint(auth.bp)
    
    # initialize database
    with app.app_context():
        db_name = 'database.db'
        db = Database(db_name)
        db.close()

    # initialize SocketIO, used for broadcasting scoore
    socketio.init_app(app, 
        cors_allowed_origins="*",
        logger=True,
        engineio_logger=True,
        async_mode='eventlet'  # make sure its eventlet async_mode
    )
    
    return app