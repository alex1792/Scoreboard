from flask import jsonify, Blueprint
from .models import Tournament, Format, Event, Group
from .models import db
from .utils import check_authorization
from flask_jwt_extended import jwt_required
from flask import request
from datetime import datetime
from .services.tournament_service import TournamentService
"""
This file contains the functions for the tournament blueprint. 
"""

tournament_bp = Blueprint('tournament', __name__, url_prefix='/api/tournaments')

"""
This function is  used to get all tournaments information in the database.
It will return all the tournaments info to the frontend. Then the frontend
will display all the tournaments in the /tournaments page.
"""
@tournament_bp.route('/', methods=['GET'])
def get_tournaments():
    """get all tournaments info from tournament_service"""
    try:
        tournaments_data = TournamentService.get_all_tournaments()
        if not tournaments_data:
            return jsonify({"status": "error", "message": "No tournaments found"}), 404
        
        return jsonify({
            "status": "success", 
            "message": "Tournaments fetched successfully", 
            "data": tournaments_data
        }), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to get tournaments"}), 500



"""
This function is  used to get the details of a specific tournament. Search by tournament_id.
It will return the details of the tournament, including the id, name, start_date, end_date, 
location, status, events. This info will be uesed to show the tournamet details in the /tournaments/<int:tournament_id> page.
"""
@tournament_bp.route('/<int:tournament_id>', methods=['GET'])
def get_tournament_details(tournament_id):
    """get tournament details from tournament_service"""
    try:
        tournament_data = TournamentService.get_tournament_by_id(tournament_id)
        if not tournament_data:
            return jsonify({"status": "error", "message": "Tournament not found"}), 404
        
        return jsonify({
            "status": "success", 
            "message": "Tournament details fetched successfully", 
            "data": tournament_data
        }), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to get tournament details"}), 500


"""
This function is used to create a new tournament. It will create a new tournament record in the database.
"""
@tournament_bp.route('/create_tournament', methods=['POST'])
@jwt_required()
def create_tournament():
    """create tournament from tournament_service"""
    try:
        auth = check_authorization()
        if auth:
            return auth
    except Exception as e:
        return jsonify({"status": "error", "message": "Please Login to create a tournament"}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No tournament data provided"}), 400

        tournament_info = data.get('tournament')
        events_info = data.get('events')

        if not tournament_info or not events_info:
            return jsonify({"status": "error", "message": "Missing tournament or events data"}), 400
        
        tournament = TournamentService.create_tournament(tournament_info, events_info)
        return jsonify({"status": "success", "message": "Tournament created successfully"}), 200
        
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Error creating tournament"}), 500