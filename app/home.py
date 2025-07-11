from flask import jsonify, Blueprint
# from .blueprints import home_bp

home_bp = Blueprint('home', __name__, url_prefix='/api/home')

"""
This file contains the functions for the home blueprint.
"""

@home_bp.route('/')
def home():
    return jsonify({"status": "success", "message": "Welcome to Scoreboard API"})