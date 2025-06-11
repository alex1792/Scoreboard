from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .blueprints import (
    home_blueprint, scoreboard_blueprint, admin_blueprint,
    users_blueprint, match_blueprint, manage_match_blueprint,
    create_match_blueprint, assign_umpire_blueprint
)
from .extensions import socketio
from .models import Match, db, User

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
        "player1": match.player1.name if match.player1 else "N/A",
        "player2": match.player2.name if match.player2 else "N/A",
        "score1": match.score1,
        "score2": match.score2,
        "status": match.status,
        "umpire": match.umpire.username if match.umpire else "N/A",
        "umpire_id": match.umpire.id if match.umpire else None
    }

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
@admin_blueprint.route('/users/<username>', methods=['PUT'])
@jwt_required()
def update_user_role(username):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    if not current_user or current_user.role != 'admin':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    data = request.get_json()
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    user.role = data.get('role', user.role)
    db.session.commit()

    socketio.emit('user_role_updated', {
        "username": user.username,
        "role": user.role
    }, namespace='/admin')

    return jsonify({"status": "success", "data": user.serialize()})

# check all users
@admin_blueprint.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    # 檢查當前用戶是否是 admin
    print('\n\nget_all_users called\n\n')
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    if not current_user or current_user.role != 'admin':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

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
# query all matches fron database, and return as a list. Frontend will use this to display all
# matches
@match_blueprint.route('/')
def get_all_matches():
    matches = Match.query.all()
    data_list = [get_match_data(match) for match in matches]
    return jsonify({
        "status": "success",
        "data": data_list
    })

# WebSocket events for scoreboard updates
@socketio.on('connect', namespace='/scoreboard')
def handle_connect():
    print("[WebSocket] Client connected to /scoreboard namespace")

@socketio.on('disconnect', namespace='/scoreboard')
def handle_disconnect():
    print("[WebSocket] Client disconnected from /scoreboard namespace")

# create a new match
@match_blueprint.route('/', methods=['POST'])
@jwt_required()
def create_match():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    if not current_user or current_user.role != 'admin':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    data = request.get_json()
    player1 = User.query.filter_by(username=data['player1']).first()
    player2 = User.query.filter_by(username=data['player2']).first()

    if not all([player1, player2]):
        return jsonify({"status": "error", "message": "Players not found"}), 404

    new_match = Match(
        player1_id=player1.id,
        player2_id=player2.id,
        status='Scheduled'
    )
    db.session.add(new_match)
    db.session.commit()

    return jsonify({
        "status": "success",
        "data": get_match_data(new_match)
    }), 201

# ================== 裁判分配路由 ==================
@match_blueprint.route('/<int:match_id>/umpire', methods=['PUT'])
@jwt_required()
def assign_umpire(match_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    if not current_user or current_user.role != 'admin':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    data = request.get_json()
    match = Match.query.get(match_id)
    umpire = User.query.get(data['umpire_id'])

    if not all([match, umpire]):
        return jsonify({"status": "error", "message": "Not found"}), 404

    match.umpire_id = umpire.id
    db.session.commit()

    socketio.emit('match_update', get_match_data(match), namespace='/scoreboard')

# ================== return umpire's match id ==================
@match_blueprint.route('/umpire/<int:umpire_id>', methods=['GET'])
def get_match_by_umpire(umpire_id):
    # 假設一位裁判同時只負責一場比賽，且 status 為 ongoing
    match = Match.query.filter_by(umpire_id=umpire_id, status='ongoing').first()
    if not match:
        return jsonify({"status": "error", "message": "No match found for this umpire"}), 404
    return jsonify({"status": "success", "data": {"id": match.id}})


@match_blueprint.route('/<int:match_id>', methods=['GET'])
def get_match_scoreboard(match_id):
    match = Match.query.get(match_id)
    if not match:
        return jsonify({"status": "error", "message": "No match found"}), 404
    return jsonify({"status": "success", "data": get_match_data(match)})

@match_blueprint.route('/<int:match_id>/score', methods=['POST'])
@jwt_required()
def update_score(match_id):
    print(f'\n\nUpdating score for Match ID: {match_id}\n')
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    if not current_user or current_user.role not in ['umpire', 'admin']:
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    data = request.get_json()
    action_type = data.get('action_type')

    print(data)
    
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