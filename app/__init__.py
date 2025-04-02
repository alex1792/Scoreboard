from flask import Flask
from config import Config
from flask_login import LoginManager, current_user
from .db import Database, load_user
from .routes import home_blueprint, scoreboard_blueprint, umpire_blueprint

login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    # app.register_blueprint(routes_app)

    # initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)

    # define user_loader function
    @login_manager.user_loader
    def load_user_wrapper(user_id):
        return load_user(user_id)

    # register blueprints
    app.register_blueprint(home_blueprint)
    app.register_blueprint(scoreboard_blueprint)
    app.register_blueprint(umpire_blueprint)
    
    # initialize database
    with app.app_context():
        db_name = 'database.db'
        db = Database(db_name)
        db.close()
    
    return app