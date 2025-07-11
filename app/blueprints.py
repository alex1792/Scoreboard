from flask import Blueprint
from .home import home_bp
from .auth import auth_bp
from .tournament import tournament_bp
from .registration import registration_bp
from .match import match_bp
from .admin import admin_bp
from .user import user_bp
from .file import file_bp
from .scoreboard import scoreboard_bp


def register_blueprints(app):
    blueprints = [
        home_bp,
        auth_bp,
        tournament_bp,
        registration_bp,
        match_bp,
        admin_bp,
        user_bp,
        file_bp,
        scoreboard_bp,
    ]
    for blueprint in blueprints:
        app.register_blueprint(blueprint    )