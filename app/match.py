from flask import jsonify, request, Blueprint
from .models import Match, User, db
from .utils import check_authorization, get_match_data
from .extensions import socketio
from flask_jwt_extended import jwt_required, get_jwt_identity   
from .utils import create_match_record, get_match_data
from .services.match_service import MatchService

"""
This file contains the functions for the match blueprint.
"""

match_bp = Blueprint('match', __name__, url_prefix='/api/matches')

"""
This function is used to get all the matches of a tournament. It will return all the match info
to the frontend. Then, the frontend will show all the matches in the /matches page.
"""
@match_bp.route('/')
def get_all_matches():
    try:
        data_list = MatchService.get_all_matches()
        return jsonify({
            "status": "success",
            "data": data_list
        })
    except Exception as e:
        return jsonify({"status": "error", "message": "Failed to get all matches"}), 500
    
# ----------------------------------------------------------------------

"""
This function is used to create a new match. It will create a new match record in the database.
It will return the match info to the frontend. Then, the frontend will show the match in the /matches page.
"""
# ------------------------- create a new match ---------------------------
@match_bp.route('/create_match', methods=['POST'])
@jwt_required()
def create_match():
    try:
        authorization = check_authorization()
        if authorization:
            return authorization

        data = request.get_json()
        match_data = {
            'player1_name': data['player1_username'],
            'player2_name': data['player2_username'],
            'category': data['category'],
            'status': 'Scheduled'
        }

        new_match_data = MatchService.create_match(match_data)
        # new_match_data = create_match_record(data['player1_username'], data['player2_username'], data['category'], 'Scheduled')

        return jsonify({
            "status": "success",
            "data": new_match_data
        }), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to create match"}), 500

    

"""
This function is used to assign an umpire to a specific match. It will update the umpire_id of the match.
It will return the match info to the frontend. Then, the frontend will show the match in the /matches page.
"""
# ----------------- Assign umpire to specific game ---------------------
@match_bp.route('/<int:match_id>/umpire', methods=['POST'])
@jwt_required()
def assign_umpire(match_id):
    try:
        authorization = check_authorization()
        if authorization:
            return authorization

        data = request.get_json()
        umpire_id = data['umpire_id']

        match_data = MatchService.assign_umpire(match_id, umpire_id)
        
        # Socket.IO broadcast the updated match info to the frontend
        socketio.emit('match_update', match_data, namespace='/scoreboard')

        return jsonify({"status": "success", "data": match_data}), 200
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to assign umpire"}), 500


"""
This funciton is used to get the match by umpire_id, it will return the match info to the frontend.
For example, given umpire_id, the function will return the match that the umpire is assigned to. Which
means the returned match is the match that the umpire should umpire.
"""
@match_bp.route('/umpire/<int:umpire_id>', methods=['GET'])
def get_match_by_umpire(umpire_id):
    try:
        match_data = MatchService.get_matches_by_umpire(umpire_id)
        if not match_data:
            return jsonify({"status": "error", "message": "No match found for this umpire"}), 404
        return jsonify({"status": "success", "data": {"id": match_data['id']}})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to get match by umpire"}), 500
# ----------------------------------------------------------------------


"""
This function is used to get the match by match_id. It will return the specific match
info to frontend.
"""
# ----------------------------------------------------------------------
@match_bp.route('/<int:match_id>', methods=['GET'])
def get_match_scoreboard(match_id):
    try:
        match = MatchService.get_match_by_id(match_id)
        if not match:
            return jsonify({"status": "error", "message": "No match found"}), 404
        return jsonify({"status": "success", "data": match})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to get match by umpire"}), 500
# ----------------------------------------------------------------------

"""
This function is used to update the score of specific match. After updating the score,
backend will broadcast the updated score to the frontend. And the frontend will show the 
updated score at the scoreboard at the same time.

The emit() function is the core function of the real-time scoreboard. We need to use this
function to achieve the real-time scoreboard.
"""
# ----------------------------------------------------------------------
@match_bp.route('/<int:match_id>/score', methods=['POST'])
@jwt_required()
def update_score(match_id):
    try:
        authorization = check_authorization("umpire")
        if authorization:
            return authorization

        data = request.get_json()
        action_type = data.get('action_type')
        
        if action_type == 'update_score':
            player = data.get('player')
            score = int(data.get('score'))
            match_data = MatchService.update_score(match_id, player, score)
        elif action_type == 'change_status':
            new_status = data.get('new_status')
            match_data = MatchService.update_match_status(match_id, new_status)
        else:
            return jsonify({"status": "error", "message": "Invalid action type"}), 400

        # Socket.IO broadcast
        socketio.emit('match_update', match_data, namespace='/scoreboard')
        
        return jsonify({"status": "success", "data": match_data})
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to update score"}), 500

# ----------------------------------------------------------------------

"""
This function is used to clear all the matches in the database. However, it is not used in
the current version. The current version has more complex database structure, so it is not
used. It can be modified to clear all the match of a particular tournament.
"""
@match_bp.route('/clear_all_match', methods=['POST'])
@jwt_required()
def clear_all_matches():
    try:
        authorization = check_authorization()
        if authorization:
            return authorization
            
        MatchService.clear_all_matches()
        return jsonify({"status": "success", "message": "All matches cleared"}), 200
    except Exception as e:
        print(f"Error clearing matches: {e}")
        return jsonify({"status": "error", "message": "Failed to clear matches"}), 500
# ----------------------------------------------------------------------    

"""
This function is used to delete a specific match. However, it is not used in
the current version. It must be modified to achieve the function goal.
"""
# ----------------------------------------------------------------------
@match_bp.route('/<int:match_id>', methods=['DELETE'])
@jwt_required()
def delete_match(match_id):
    # delete match by match_id
    try:
        # check authorization
        authorization = check_authorization()
        if authorization:
            return authorization
        
        MatchService.delete_match(match_id)
        return jsonify({"status": "success", "message": f"delete #{match_id} match successfully"})
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to delete match"}), 500
# ----------------------------------------------------------------------  

# socket io
"""
This function is used to handle the WebSocket connection for the scoreboard updates.
It will print the connection and disconnection events.
"""
# ------------- WebSocket events for scoreboard updates ----------------
@socketio.on('connect', namespace='/scoreboard')
def handle_scoreboard_connect():
    print("[WebSocket] Client connected to /scoreboard namespace")

@socketio.on('disconnect', namespace='/scoreboard')
def handle_scoreboard_disconnect():
    print("[WebSocket] Client disconnected from /scoreboard namespace")
# ----------------------------------------------------------------------