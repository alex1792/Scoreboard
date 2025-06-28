from flask import request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from .blueprints import (
    home_blueprint, scoreboard_blueprint, admin_blueprint,
    users_blueprint, match_blueprint, manage_match_blueprint,
    create_match_blueprint, assign_umpire_blueprint
)
from .extensions import socketio
from .models import Match, db, User
from .scheduler import generate_schedule
import os

# ===============================================================================================
# ===============================================================================================
# ===============================================================================================
# ===============================================================================================
# ===============================================================================================
# ===================================== general function ========================================
# ===============================================================================================
# ===============================================================================================
# ===============================================================================================
# ===============================================================================================
def get_match_data(match):
    return {
        "id": match.id,
        "category": match.category,
        "player1": match.player1_name if match.player1_name else "N/A",
        "player2": match.player2_name if match.player2_name else "N/A",
        # "player1_id": match.player1.id if match.player1 else None,
        # "player2_id": match.player2.id if match.player2 else None,
        "score1": match.score1,
        "score2": match.score2,
        "status": match.status,
        "umpire": match.umpire.username if match.umpire else "N/A",
        "umpire_id": match.umpire.id if match.umpire else None
    }

def create_match_record(player1_name, player2_name, category, status='Scheduled'):
    new_match = Match(**{
        'player1_name': player1_name,
        'player2_name': player2_name,
        'category': category,
        'status': status
    })
    db.session.add(new_match)
    db.session.commit()
    return new_match

def check_authorization(role='admin'):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # check if not admin, return error
    if not current_user or (current_user.role != 'admin' and current_user.role != role):
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    return None

# ===============================================================================================
# ===============================================================================================
# ===============================================================================================
# ===============================================================================================
# ===============================================================================================
# ======================================= home blueprint ========================================
# ===============================================================================================
# ===============================================================================================
# ===============================================================================================
# ===============================================================================================
@home_blueprint.route('/')
def home():
    return jsonify({"status": "success", "message": "Welcome to Scoreboard API"})

# ===============================================================================================
# ===============================================================================================
# ===============================================================================================
# ===============================================================================================
# ===============================================================================================
# ======================================= admin_blueprint =======================================
# ===============================================================================================
# ===============================================================================================
# ===============================================================================================
# ===============================================================================================
@admin_blueprint.route('/users', methods=['PUT'])
@jwt_required()
def update_user_role():
    # check if user is authorized
    authorization = check_authorization()
    if authorization:
        return authorization

    data = request.get_json()
    print(f'\n\ndata: ${data}\n')

    user_id = data.get('user_id')
    new_role = data.get('new_role')

    if not user_id or not new_role:
        return jsonify({"status": "error", "message": "Missing user_id or new_role"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    user.role = new_role
    db.session.commit()

    print(f"User {user.username} role updated to {user.role}")

    socketio.emit('user_role_updated', {
        "username": user.username,
        "role": user.role
    }, namespace='/update_user_role')

    return jsonify({"status": "success", "data": user.serialize()})

# check all users
@admin_blueprint.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    # check if user is authorized
    authorization = check_authorization()
    if authorization:
        return authorization

    users = User.query.all()
    users_data = [
        {
            "id": user.id,
            "username": user.username,
            "is_judge": user.is_judge,
            "role": user.role
        }
        for user in users
    ]
    return jsonify({
        "status": "success",
        "data": users_data
    })
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
@admin_blueprint.route('/upate_user_role', methods=['PUT'])
@jwt_required()
def update_user_roles():
    # check if user is authorized
    authorization = check_authorization()
    if authorization:
        return authorization
    
    # get user from request
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    role = data.get('role')

    # update user role
    if user:
        user.role = role
        db.session.commit()
    
    # broadcast to all connected clients
    socketio.emit('user_role_updated', {
        "username": user.username if user else None,
        "role": user.role if user else None
    }, namespace='/user_role_update')

    # return success response
    return jsonify({
        "status": "success",
        "message": f"User {user.username if user else None} role updated to {role}"
    }), 200

# ------------- WebSocket events for user role updates ----------------
@socketio.on('connect', namespace='/user_role_update')
def handle_connect():
    print("[WebSocket] Client connected to /user_role_update namespace")

@socketio.on('disconnect', namespace='/user_role_update')
def handle_disconnect():
    print("[WebSocket] Client disconnected from /user_role_update namespace")
# ----------------------------------------------------------------------

@admin_blueprint.route('/upload_match_schedule', methods=['POST'])
@jwt_required()
def upload_match_schedule():
    # check if user is authorized
    authorization = check_authorization()
    if authorization:
        return authorization
    
    file = request.files.get('file')
    if not file or not file.filename:
        return jsonify({"status": "error", "message": "No file provided"}), 400
    if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
        return jsonify({"status": "error", "message": "Invalid file format, only .csv and .xslx are allowed"}), 400

    try:
        import pandas as pd
        if file.filename.endswith('.csv'):
            f = pd.read_csv(file.stream, encoding='utf-8')
        else:
            f = pd.read_excel(file.stream, engine='openpyxl')
        
        player1s = f['player1'].tolist()
        player2s = f['player2'].tolist()
        categories = f['category'].tolist()

        created_matches = []
        for player1, player2, category in zip(player1s, player2s, categories):
            print(player1, player2, category)
            match = create_match_record(player1, player2, category)
            created_matches.append(get_match_data(match))

        return jsonify({"status": "success", "message": "Matches created successfully", "matches": created_matches}), 200
    except Exception as e:
        print(f"Error reading file: {e}")   
        return jsonify({"status": "error", "message": "Failed to read the file"}), 500

    # return jsonify({"status": "success", "message": "File uploaded successfully"}), 200

@admin_blueprint.route('/upload_round_robin', methods=['POST'])
@jwt_required()
def generate_match_schedule():
    # check authorization
    auth = check_authorization()
    if auth:
        return auth
    
    print("Generating round robin schedule...")
    # scheduling algo
    try:
        # read .xlsx or .csv file
        file = request.files.get('file')

        # get total court from frontend (Default: 6)
        total_court = request.form.get('total_court', 6)
        try:
            total_court = int(total_court)
        except (ValueError, TypeError):
            total_court = 6

        if not file or not file.filename:
            return jsonify({"status": "error", "message": "No file provided"}), 400
        if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
            return jsonify({"status": "error", "message": "Invalid file format, only .csv and .xslx are allowed"}), 400

        import pandas as pd
        if file.filename.endswith('.csv'):
            f = pd.read_csv(file.stream, encoding='utf-8')
        else:
            f = pd.read_excel(file.stream, engine='openpyxl')

        instance_path = current_app.instance_path
        output_path = os.path.join(instance_path, 'round_robin_schedule.xlsx')
        
        # total_court = 6
        generate_schedule(f, total_court, output_path)

        return send_file(output_path, as_attachment=True, download_name='round_robin_schedule.xlsx')

    except Exception as e:
        print(f"Error creating match schedule: {e}")
        return jsonify({"status": "error", "message": "Error creating match schedule"})


# ===============================================================================================
# ===============================================================================================
# ===============================================================================================
# ===============================================================================================
# ===============================================================================================
# ======================================= match blueprint =======================================
# ===============================================================================================
# ===============================================================================================
# ===============================================================================================
# ===============================================================================================

# ------------- query all matches fron database, and return  -------------
# ------------- as a list. Frontend will use this to display -------------
# ----------------------------- all matches ------------------------------
# 
@match_blueprint.route('/')
def get_all_matches():
    matches = Match.query.all()
    data_list = [get_match_data(match) for match in matches]
    return jsonify({
        "status": "success",
        "data": data_list
    })
# ----------------------------------------------------------------------

# ------------- WebSocket events for scoreboard updates ----------------
@socketio.on('connect', namespace='/scoreboard')
def handle_scoreboard_connect():
    print("[WebSocket] Client connected to /scoreboard namespace")

@socketio.on('disconnect', namespace='/scoreboard')
def handle_scoreboard_disconnect():
    print("[WebSocket] Client disconnected from /scoreboard namespace")
# ----------------------------------------------------------------------

# ------------------------- create a new match ---------------------------
@match_blueprint.route('/create_match', methods=['POST'])
@jwt_required()
def create_match():
    # check if user is authorized
    authorization = check_authorization()
    if authorization:
        return authorization

    data = request.get_json()
    # player1 = User.query.filter_by(username=data['player1_username']).first()
    # player2 = User.query.filter_by(username=data['player2_username']).first()
    

    # if not all([player1, player2]):
    #     return jsonify({"status": "error", "message": "Players not found"}), 404

    new_match = Match(**{
        'player1_name':data['player1_username'],
        'player2_name': data['player2_username'],
        'category': data['category'],
        'status': 'Scheduled'
    })
    db.session.add(new_match)
    db.session.commit()

    return jsonify({
        "status": "success",
        "data": get_match_data(new_match)
    }), 201
# ----------------------------------------------------------------------

# ----------------- Assign umpire to specific game ---------------------
@match_blueprint.route('/<int:match_id>/umpire', methods=['POST'])
@jwt_required()
def assign_umpire(match_id):
    # check if user is authorized
    authorization = check_authorization()
    if authorization:
        return authorization

    data = request.get_json()
    match = Match.query.get(match_id)
    umpire = User.query.get(data['umpire_id'])

    if not match:
        return jsonify({"status": "error", "message": "Match not found"}), 404
    if not umpire:
        return jsonify({"status": "error", "message": "Umpire not found"}), 404
    
    match.umpire_id = umpire.id if umpire else None
    db.session.commit()

    socketio.emit('match_update', get_match_data(match), namespace='/scoreboard')

    return jsonify({"status": "success", "data": get_match_data(match)}), 200
# ----------------------------------------------------------------------

# ------------------- return umpire's match id -------------------------
@match_blueprint.route('/umpire/<int:umpire_id>', methods=['GET'])
def get_match_by_umpire(umpire_id):
    # 假設一位裁判同時只負責一場比賽，且 status 為 ongoing
    # match = Match.query.filter_by(umpire_id=umpire_id, status='ongoing').first()
    match = Match.query.filter_by(umpire_id=umpire_id).first()
    if not match:
        return jsonify({"status": "error", "message": "No match found for this umpire"}), 404
    return jsonify({"status": "success", "data": {"id": match.id}})
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
@match_blueprint.route('/<int:match_id>', methods=['GET'])
def get_match_scoreboard(match_id):
    match = Match.query.get(match_id)
    if not match:
        return jsonify({"status": "error", "message": "No match found"}), 404
    return jsonify({"status": "success", "data": get_match_data(match)})
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
@match_blueprint.route('/<int:match_id>/score', methods=['POST'])
@jwt_required()
def update_score(match_id):
    # check if user is authorized
    authorization = check_authorization("umpire")
    if authorization:
        return authorization

    data = request.get_json()
    action_type = data.get('action_type')
    
    match = Match.query.get(match_id)
    if not match:
        return jsonify({"status": "error", "message": "No active match"}), 404

    if action_type == 'update_score':
        player = data.get('player')
        score = int(data.get('score'))
        if player == 'Player1':
            match.score1 += score
        else:
            match.score2 += score
    elif action_type == 'change_status':
        match.status = data.get('new_status')

    db.session.commit()

    # Socket.IO 廣播
    socketio.emit('match_update', get_match_data(match), namespace='/scoreboard')
    
    return jsonify({"status": "success", "data": get_match_data(match)})
# ----------------------------------------------------------------------

@match_blueprint.route('/clear_all_match', methods=['POST'])
@jwt_required()
def clear_all_matches():
    # check if user is authorized
    authorization = check_authorization()
    if authorization:
        return authorization
    
    try:
        Match.query.delete()
        db.session.commit()
        return jsonify({"status": "success", "message": "All matches cleared"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error clearing matches: {e}")
        return jsonify({"status": "error", "message": "Failed to clear matches"}), 500
# ----------------------------------------------------------------------    

# ----------------------------------------------------------------------
@match_blueprint.route('/<int:match_id>', methods=['DELETE'])
@jwt_required()
def delete_match(match_id):
    # check authorization
    authorization = check_authorization()
    if authorization:
        return authorization

    # delete match by match_id
    try:
        Match.query.filter_by(id=match_id).delete()
        db.session.commit()
        return jsonify({"status": "success", "message": f"delete #{match_id} match successfully"})
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting #{match_id} match: {e}")
        return jsonify({"status": "error", "message": f"Failed to delete #{match_id} match"})
# ----------------------------------------------------------------------  
