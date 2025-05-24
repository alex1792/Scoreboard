import functools
import sqlite3
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from .blueprints import (home_blueprint, scoreboard_blueprint, umpire_blueprint, 
                         admin_blueprint, users_blueprint, match_blueprint, 
                         manage_match_blueprint, create_match_blueprint, clear_all_match_blueprint,
                         change_match_status_blueprint, assign_umpire_blueprint)
# from .models import Database
from .form import ScoreForm
from .extensions import socketio

app = Flask(__name__)
app.config['DATABASE'] = 'database.db'

# @home_blueprint.route('/')
# def home():
#     # print(f"Is authenticated: {current_user.is_authenticated}")
#     if current_user.is_authenticated:
#         return render_template('scoreboard/home.html', user=current_user.username)
#     else:
#         return render_template('scoreboard/home.html')

@home_blueprint.route('/')
def home():
    return render_template('scoreboard/home.html')


# @scoreboard_blueprint.route('/scoreboard')
# def index():
#     db_name = 'database.db'
#     db = Database(db_name)
#     match_info = db.get_match_info()
#     db.close()
    
#     if match_info:
#         match_id = match_info['match_id']
#         player1_name = match_info['player1_name']
#         player2_name = match_info['player2_name']
#         score1 = match_info['score1']
#         score2 = match_info['score2']
#         status = match_info['status']
#         # umpire_name = match_info['umpire_name']
#         return render_template('scoreboard/scoreboard.html', player1_name=player1_name, player2_name=player2_name, score1=score1, score2=score2, match_id=match_id, match_status=status)
#     else:
#         return "No match found."

from .models import Match, Player
@scoreboard_blueprint.route('/scoreboard')
def index():
    match = Match.query.order_by(Match.id.desc()).first()
    if match:
        player1_name = match.player1.name if match.player1 else "N/A"
        player2_name = match.player2.name if match.player2 else "N/A"
        return render_template(
            'scoreboard/scoreboard.html',
            player1_name=player1_name,
            player2_name=player2_name,
            score1=match.score1,
            score2=match.score2,
            match_id=match.id,
            match_status=match.status
        )
    else:
        return "No match found."

    
# @scoreboard_blueprint.route('/update_score', methods=['POST'])
# @login_required
# def update_score():
#     action_type = request.form.get('action_type')

#     db_name = 'database.db'
#     db = Database(db_name)
#     match_info = db.get_match_info()
    
#     if action_type == 'update_score':
#         if match_info:        
#             player = request.form.get('player') # player belongs to the set {Player1, Player2}
#             score = int(request.form.get('score'))
#             if player == 'Player1':
#                 player1_id = match_info['player1_id']
#                 db.update_score(player1_id, match_info, score)
#             else:
#                 player2_id = match_info['player2_id']
#                 db.update_score(player2_id, match_info, score)

#     elif action_type == 'change_status':
#         new_status = request.form.get('new_status')
#         match_id = request.form.get('match_id')
#         db.change_match_status(new_status, match_id)

#     # broadcast updated score to all clients viewing the this match
#     match_info = db.get_match_info()
#     data = {'match_id': str(match_info['match_id']), 'score1': match_info['score1'], 'score2': match_info['score2'], 'match_status': match_info['status']}
#     socketio.emit('match_update', data,namespace='/scoreboard', room=None, include_self=True)

#     # close database connection
#     db.close()

#     # instead of render the page, we should use redirect
#     return redirect(url_for('scoreboard_blueprint.index'))

from .models import db, Match

@scoreboard_blueprint.route('/update_score', methods=['POST'])
@login_required
def update_score():
    action_type = request.form.get('action_type')
    match = Match.query.order_by(Match.id.desc()).first()
    if not match:
        return redirect(url_for('scoreboard_blueprint.index'))

    if action_type == 'update_score':
        player = request.form.get('player')
        score = int(request.form.get('score'))
        if player == 'Player1':
            match.score1 = score
        else:
            match.score2 = score
    elif action_type == 'change_status':
        new_status = request.form.get('new_status')
        match.status = new_status

    db.session.commit()

    # 廣播分數
    data = {
        'match_id': str(match.id),
        'score1': match.score1,
        'score2': match.score2,
        'match_status': match.status
    }
    socketio.emit('match_update', data, namespace='/scoreboard', room=None, include_self=True)
    return redirect(url_for('scoreboard_blueprint.index'))


# Handle WebSocket connection event
@socketio.on('connect', namespace='/scoreboard')
def handle_connect():
    # socketio = get_socketio()
    print(f"New client connected: {request.sid}")
    if current_user.is_authenticated:
        print(f"User {current_user.username} has connected to the live scoreboard")
    else:
        print("An anonymous user has connected to the live scoreboard")
    
    # 可选：将用户加入特定房间（如需分区广播）
    # join_room('global_scoreboard')

@socketio.on('disconnect', namespace='/scoreboard')
def handle_disconnect():
    print(f"User {request.sid} has disconnected with the live scoreboard")


# @admin_blueprint.route('/admin', methods=['POST', 'GET'])
# def set_umpire():
#     if request.method == 'POST':
#         username = request.form['username']
#         is_judge = request.form['is_judge'] == 'true'
        
#         # connect to database and update the user is_judge status
#         db = Database('database.db')
#         db.set_umpire(username, is_judge)
#         db.close()
        
#         # broadcast to the user so the stataus is now changed
#         data = {'username':username, 'is_judge':is_judge}
#         socketio.emit('user_role_updated', data, namespace='/admin', room=None, include_self=True)
        
#         # redirect to home
#         return redirect(url_for('home_blueprint.home'))
#     else:
#         return render_template('scoreboard/admin.html')

from .models import db, User

@admin_blueprint.route('/admin', methods=['POST', 'GET'])
def set_umpire():
    if request.method == 'POST':
        username = request.form['username']
        is_judge = request.form['is_judge'] == 'true'
        user = User.query.filter_by(username=username).first()
        if user:
            user.is_judge = is_judge
            db.session.commit()
            data = {'username': username, 'is_judge': is_judge}
            socketio.emit('user_role_updated', data, namespace='/admin', room=None, include_self=True)
        return redirect(url_for('home_blueprint.home'))
    else:
        return render_template('scoreboard/admin.html')

    
@socketio.on('connect', namespace='/admin')
def admin_connect():
    print("User is connected to /admin namespace")


# @users_blueprint.route('/users')
# def query_users():
#     db = Database('database.db')
#     all_users = db.get_all_users()
#     db.close()
#     return render_template('scoreboard/users.html', users=all_users)

@users_blueprint.route('/users')
def query_users():
    users = User.query.all()
    return render_template('scoreboard/users.html', users=users)


# @manage_match_blueprint.route('/manage_match', methods=['POST', 'GET'])
# def manage_match():
#     db = Database('database.db')
    
#     if request.method == 'POST':
#         match_id = request.form['match_id']
#         db.clear_match_by_id(match_id)
#         db.close()
#         return redirect(url_for('match_blueprint.query_matches'))  # 重定向到 GET, follow PRG mode (POST/REDIRECT/GET)

#     else:
#         db.close()
#         return render_template('scoreboard/manage_match.html')

from .models import db, Match

@manage_match_blueprint.route('/manage_match', methods=['POST', 'GET'])
def manage_match():
    if request.method == 'POST':
        match_id = request.form['match_id']
        match = Match.query.get(match_id)
        if match:
            db.session.delete(match)
            db.session.commit()
        return redirect(url_for('match_blueprint.query_matches'))
    else:
        return render_template('scoreboard/manage_match.html')

# @match_blueprint.route('/match')
# def query_matches():
#     db = Database('database.db')
#     all_matches = db.get_all_match()
#     db.close()
#     return render_template('scoreboard/matches.html', matches=all_matches)

@match_blueprint.route('/match')
def query_matches():
    matches = Match.query.all()
    return render_template('scoreboard/matches.html', matches=matches)


# @create_match_blueprint.route('/create_match', methods=['POST', 'GET'])
# def create_match():
#     if request.method == 'POST':
#         player1_username = request.form['player1_username']
#         player2_username = request.form['player2_username']

#         # query ids of player1 and player2
#         db = Database('database.db')
#         player1_id = db.get_user_id_by_username(player1_username)
#         player2_id = db.get_user_id_by_username(player2_username)

#         # add match
#         db.add_match(player1_id, player2_id)
#         db.close()
#         return redirect(url_for('create_match_blueprint.create_match'))
#     else:
#         return render_template('scoreboard/create_match.html')

@create_match_blueprint.route('/create_match', methods=['POST', 'GET'])
def create_match():
    if request.method == 'POST':
        player1_username = request.form['player1_username']
        player2_username = request.form['player2_username']
        player1 = User.query.filter_by(username=player1_username).first()
        player2 = User.query.filter_by(username=player2_username).first()
        if player1 and player2:
            new_match = Match(player1_id=player1.id, player2_id=player2.id)
            db.session.add(new_match)
            db.session.commit()
        return redirect(url_for('create_match_blueprint.create_match'))
    else:
        return render_template('scoreboard/create_match.html')

    
# @clear_all_match_blueprint.route('/clear_match', methods=['POST'])
# def clear_all_match():
#     db = Database('database.db')
#     db.clear_all_match()
#     db.close()
#     return redirect(url_for('manage_match_blueprint.manage_match'))

# # @change_match_status_blueprint.route('/change_match_status', methods=['POST'])
# # def change_match_status():
    # new_status = request.form['new_status']
    # match_id = request.form['match_id']
    # db = Database('database.db')
    # db.change_match_status(new_status, match_id)
    # db.close()

    # # broadcast
    # socketio.emit('match_status_update', {'match_id': str(match_id), 'match_status': new_status}, namespace='/scoreboard', include_self=True)

    # return redirect(url_for('scoreboard_blueprint.index', match_id=match_id))

@clear_all_match_blueprint.route('/clear_match', methods=['POST'])
def clear_all_match():
    Match.query.delete()
    db.session.commit()
    return redirect(url_for('manage_match_blueprint.manage_match'))


# @assign_umpire_blueprint.route('/assign_umpire')
# def assign_umpire():
#     db = Database('database.db')
#     all_matches = db.get_all_match()
#     db.close()
#     return render_template('scoreboard/assign_umpire.html', matches=all_matches)

# @assign_umpire_blueprint.route('/assign_umpire/<int:match_id>', methods=['POST'])
# def set_umpire(match_id):
#     try:
#         umpire_name = request.form.get('umpire_name')
#         for i in range(10):
#             print(umpire_name)
        
#         if not umpire_name:
#             return redirect(url_for('assign_umpire_blueprint.assign_umpire'))
        
#         # connect to database and update the match info
#         db = Database('database.db')
#         match_info = db.get_match_info()
#         db.update_score(None, match_info, None, umpire_name)

#         # broadcast updated score to all clients viewing the this match
#         match_info = db.get_match_info()
#         data = {'match_id': str(match_info['match_id']), 'score1': match_info['score1'], 'score2': match_info['score2'], 'match_status': match_info['status'], 'umpire_name': match_info['umpire_name']}
#         socketio.emit('match_update', data,namespace='/scoreboard', room=None, include_self=True)

#         # close database connection
#         db.close()

#         # instead of render the page, we should use redirect
#         # return redirect(url_for('assign_umpire_blueprint.assign_umpire'))
    
#         return jsonify({'success': True}), 200  # 返回 JSON 而非重定向
#     except Exception as e:
#         print(f"後端錯誤: {e}")  # 在終端機查看錯誤
#         return jsonify({'success': False, 'message': str(e)}), 500

@assign_umpire_blueprint.route('/assign_umpire')
def assign_umpire():
    matches = Match.query.all()
    return render_template('scoreboard/assign_umpire.html', matches=matches)

@assign_umpire_blueprint.route('/assign_umpire/<int:match_id>', methods=['POST'])
def set_umpire(match_id):
    umpire_name = request.form.get('umpire_name')
    match = Match.query.get(match_id)
    if match and umpire_name:
        match.umpire_name = umpire_name
        db.session.commit()
        data = {
            'match_id': str(match.id),
            'score1': match.score1,
            'score2': match.score2,
            'match_status': match.status,
            'umpire_name': match.umpire_name
        }
        socketio.emit('match_update', data, namespace='/scoreboard', room=None, include_self=True)
        return jsonify({'success': True}), 200
    return jsonify({'success': False, 'message': 'Match or umpire not found'}), 400
