from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .blueprints import (
    home_blueprint, scoreboard_blueprint, admin_blueprint,
    users_blueprint, match_blueprint, manage_match_blueprint,
    create_match_blueprint, assign_umpire_blueprint
)
from .extensions import socketio
from .models import Match, db, User

# ================== 通用工具函數 ==================
def get_match_data(match):
    return {
        "id": match.id,
        "player1": match.player1.name if match.player1 else "N/A",
        "player2": match.player2.name if match.player2 else "N/A",
        "score1": match.score1,
        "score2": match.score2,
        "status": match.status,
        "umpire": match.umpire.username if match.umpire else "N/A"
    }

# ================== 首頁路由 ==================
@home_blueprint.route('/api/home')
def home():
    return jsonify({"status": "success", "message": "Welcome to Scoreboard API"})

# ================== 比分板路由 ==================
@scoreboard_blueprint.route('/api/scoreboard')
def get_scoreboard():
    match = Match.query.order_by(Match.id.desc()).first()
    if not match:
        return jsonify({"status": "error", "message": "No match found"}), 404
    return jsonify({"status": "success", "data": get_match_data(match)})

@scoreboard_blueprint.route('/api/scoreboard/update', methods=['POST'])
@jwt_required()
def update_score():
    current_user = get_jwt_identity()
    if current_user['role'] not in ['umpire', 'admin']:
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    data = request.get_json()
    action_type = data.get('action_type')
    
    match = Match.query.order_by(Match.id.desc()).first()
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

# ================== 管理員路由 ==================
@admin_blueprint.route('/api/admin/users/<username>', methods=['PUT'])
@jwt_required()
def update_user_role(username):
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
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

# ================== 比賽管理路由 ==================
@match_blueprint.route('/api/matches')
def get_all_matches():
    matches = Match.query.all()
    return jsonify({
        "status": "success",
        "data": [get_match_data(match) for match in matches]
    })

@create_match_blueprint.route('/api/matches', methods=['POST'])
@jwt_required()
def create_match():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
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
@assign_umpire_blueprint.route('/api/matches/<int:match_id>/umpire', methods=['PUT'])
@jwt_required()
def assign_umpire(match_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    data = request.get_json()
    match = Match.query.get(match_id)
    umpire = User.query.get(data['umpire_id'])

    if not all([match, umpire]):
        return jsonify({"status": "error", "message": "Not found"}), 404

    match.umpire_id = umpire.id
    db.session.commit()

    socketio.emit('match_update', get_match_data(match), namespace='/scoreboard')
