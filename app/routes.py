from flask import request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from .blueprints import (
    home_blueprint, scoreboard_blueprint, admin_blueprint,
    users_blueprint, match_blueprint, manage_match_blueprint,
    create_match_blueprint, assign_umpire_blueprint
)
from .extensions import socketio
from .models import Match, db, User, Tournament, Event, Group, Format
from .scheduler import generate_schedule
from .match_generator import generate_match
import os
from datetime import datetime

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
    if match.event_type in ['MS', 'WS']: 
        user1 = User.query.get(match.player1_id)
        user2 = User.query.get(match.player2_id)
        player1 = user1.get_full_name() if user1 else "N/A"
        player2 = user2.get_full_name() if user2 else "N/A"
    else: 
        team1_user1 = User.query.get(match.team1_player1_id)
        team1_user2 = User.query.get(match.team1_player2_id)
        team2_user1 = User.query.get(match.team2_player1_id)
        team2_user2 = User.query.get(match.team2_player2_id)
        team1_p1 =team1_user1.get_full_name() if team1_user1 else "N/A"
        team1_p2 = team1_user2.get_full_name() if team1_user2 else "N/A"
        team2_p1 = team2_user1.get_full_name() if team2_user1 else "N/A"
        team2_p2 = team2_user2.get_full_name() if team2_user2 else "N/A"
        
        player1 = f"{team1_p1} / {team1_p2}"
        player2 = f"{team2_p1} / {team2_p2}"
    
    event = Event.query.get(match.event_id) if match.event_id else None
    category = event.category if event else 'N/A'
    umpire = User.query.get(match.umpire_id)
    
    return {
        "id": match.id,
        "category": category,
        "player1": player1,
        "player2": player2,
        "score1": match.player1_score,
        "score2": match.player2_score,
        "status": match.status,
        "umpire": umpire.get_full_name() if umpire else "N/A",
        "umpire_id": match.umpire_id
    }

def create_match_record(player1_name, player2_name, category, status='Scheduled'):
    new_match = None
    if category == 'MS' or category == 'WS':
        new_match = Match(**{
            'player1_name': player1_name,
            'player2_name': player2_name,
            'category': category,
            'status': status
        })
    else:
        team1_player1_name = player1_name.split(' / ')[0]
        team1_player2_name = player1_name.split(' / ')[1]
        team2_player1_name = player2_name.split(' / ')[0]
        team2_player2_name = player2_name.split(' / ')[1]
        new_match = Match(**{
            'team1_player1_name': team1_player1_name,
            'team1_player2_name': team1_player2_name,
            'team2_player2_name': team2_player1_name,
            'team2_player2_name': team2_player2_name,
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

def print_tournament_info(tournament_name):
    tournament = Tournament.query.filter_by(name=tournament_name).first()
    if not tournament:
        return None
    
    print(f"Tournament: {tournament.name}")
    print(f"Start Date: {tournament.start_date}")
    print(f"End Date: {tournament.end_date}")
    print(f"Status: {tournament.status}")
    print(f"Events: {len(tournament.events)} events")

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

@home_blueprint.route('/tournaments', methods=['GET'])
def get_tournaments():
    try:
        tournaments = Tournament.query.all()
        if not tournaments:
            return jsonify({"status": "error", "message": "No tournaments found"}), 404
        
        tournaments_data = []
        for tournament in tournaments:
            tournament_data = {
                'id': tournament.id,
                'name': tournament.name,
                'start_date': tournament.start_date.isoformat() if tournament.start_date else None,
                'end_date': tournament.end_date.isoformat() if tournament.end_date else None,
                'location': tournament.location,
                'status': tournament.status,
                'event_count': len(tournament.events)
            }
            tournaments_data.append(tournament_data)
        return jsonify({"status": "success", "message": "Tournaments fetched successfully", "data": tournaments_data}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to get tournaments"}), 500

@home_blueprint.route('/tournaments/<int:tournament_id>', methods=['GET'])
def get_tournament_details(tournament_id):
    tournament = Tournament.query.get(tournament_id)
    if not tournament:
        return jsonify({"status": "error", "message": "Tournament not found"}), 404

    events = []
    for event in tournament.events:  # 使用關聯查詢
        groups = []
        for group in event.groups:  # 使用關聯查詢
            format = Format.query.get(group.format_id)
            group_data = {
                'id': group.id,
                'name': group.name,
                'type': format.type if format else 'N/A'
            }
            groups.append(group_data)
        
        event_data = {
            'id': event.id,
            'name': event.name,
            'category': event.category,
            'groups': groups
        }
        events.append(event_data)

    tournament_data = {
        'id': tournament.id,
        'name': tournament.name,
        'start_date': tournament.start_date.isoformat() if tournament.start_date else None,
        'end_date': tournament.end_date.isoformat() if tournament.end_date else None,
        'location': tournament.location,
        'status': tournament.status,
        'events': events
    }
    return jsonify({"status": "success", "message": "Tournament details fetched successfully", "data": tournament_data}), 200


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
    authorization = check_authorization()
    if authorization:
        return authorization

    users = User.query.all()
    users_data = [
        {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
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

@admin_blueprint.route('/upload_participants', methods=['POST'])
@jwt_required()
def upload_participants():
    # check authorization
    auth = check_authorization()
    if auth:
        return auth

    print("Generating all possible matches...")
    
    # generate match algo
    try:
        # read .xlsx or .csv file
        file = request.files.get('file')

        categories = request.form.get('categories', 'MS,WS,MD,WD,XD')
        flight = request.form.get('flight', 'A,B,C')
        rules_type = request.form.get('rules', 'r,e')

        categories = categories.split(',')
        flight = flight.split(',')

        rules = {}
        for cat in categories:
            for fl in flight:
                key = f"{cat}-{fl}"
                if rules_type == 'r':
                    rules[key] = ['r', 4]  # round-robin with 4 players per group
                else:
                    rules[key] = ['e']  # elimination

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
        os.makedirs(instance_path, exist_ok=True)
        output_path = os.path.join(instance_path, 'all_matches.xlsx')
        
        # total_court = 6
        generate_match(f, categories, flight, rules, output_path)

        return send_file(output_path, as_attachment=True, download_name='all_matches.xlsx')

    except Exception as e:
        print(f"Error creating match schedule: {e}")
        return jsonify({"status": "error", "message": "Error creating match schedule"})

@admin_blueprint.route('/create_tournament', methods=['POST'])
@jwt_required()
def create_tournament():
    auth = check_authorization()
    if auth:
        return auth

    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No tournament data provided"}), 400

        tournament_info = data.get('tournament')
        events_info = data.get('events')
        print(f"tournament_info: {tournament_info}")
        print(f"events_info: {events_info}")

        if not tournament_info or not events_info:
            return jsonify({"status": "error", "message": "Missing tournament or events data"}), 400
        
        # Convert date strings to datetime objects
        if 'start_date' in tournament_info and tournament_info['start_date']:
            try:
                tournament_info['start_date'] = datetime.fromisoformat(tournament_info['start_date'])
            except ValueError:
                return jsonify({"status": "error", "message": "Invalid start_date format"}), 400
        
        if 'end_date' in tournament_info and tournament_info['end_date']:
            try:
                tournament_info['end_date'] = datetime.fromisoformat(tournament_info['end_date'])
            except ValueError:
                return jsonify({"status": "error", "message": "Invalid end_date format"}), 400
        
        # Create tournament
        tournament = Tournament(**tournament_info)
        db.session.add(tournament)
        db.session.flush()  # 獲取 tournament.id

        # Create events
        for event_info in events_info:
            if "Men's Single" in event_info['name']:
                event_info['category'] = 'MS'
            elif "Women's Single" in event_info['name']:
                event_info['category'] = 'WS'
            elif "Men's Doubles" in event_info['name']:
                event_info['category'] = 'MD'
            elif "Women's Doubles" in event_info['name']:
                event_info['category'] = 'WD'
            elif "Mixed Doubles" in event_info['name']:
                event_info['category'] = 'XD'

            event = Event()
            event.name = event_info['name']
            event.category = event_info['category']
            event.tournament_id = tournament.id
            db.session.add(event)
            db.session.flush()  # 獲取 event.id

            # Create groups for each event
            for group_info in event_info['groups']:
                format_exist = Format.query.filter_by(type=group_info['format']).first()
                if not format_exist:
                    return jsonify({"status": "error", "message": f"Format '{group_info['format']}' not found"}), 400
                
                group = Group()
                group.name = group_info['name']
                group.event_id = event.id
                group.format_id = format_exist.id
                db.session.add(group)
        
        db.session.commit()
        return jsonify({"status": "success", "message": "Tournament created successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Error creating tournament"}), 500
        

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
