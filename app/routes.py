import functools
from flask import render_template, redirect, url_for, request
from flask_login import current_user, login_required
from .blueprints import home_blueprint, scoreboard_blueprint, umpire_blueprint
from .db import Database
from .form import ScoreForm
from .extensions import socketio


@home_blueprint.route('/')
def home():
    # print(f"Is authenticated: {current_user.is_authenticated}")
    if current_user.is_authenticated:
        return render_template('scoreboard/home.html', user=current_user.username)
    else:
        return render_template('scoreboard/home.html')


@scoreboard_blueprint.route('/scoreboard')
def index():
    db_name = 'database.db'
    db = Database(db_name)
    match_info = db.get_match_info()
    
    if match_info:
        player1_name = match_info['player1_name']
        player2_name = match_info['player2_name']
        score1 = match_info['score1']
        score2 = match_info['score2']
        return render_template('scoreboard/scoreboard.html', player1_name=player1_name, player2_name=player2_name, score1=score1, score2=score2)
    else:
        return "No match found."
    
@scoreboard_blueprint.route('/update_score', methods=['POST'])
@login_required
def update_score():
    player = request.form.get('player') # player belongs to the set {Player1, Player2}
    print(player)
    
    db_name = 'database.db'
    db = Database(db_name)
    match_info = db.get_match_info()
    

    if match_info:        
        if player == 'Player1':
            player1_id = match_info['player1_id']
            db.update_score(player1_id, match_info)
        else:
            player2_id = match_info['player2_id']
            db.update_score(player2_id, match_info)
        
        # broadcast updated score to all clients viewing the this match
        match_info = db.get_match_info()
        data = {'score1': match_info['score1'], 'score2': match_info['score2']}
        print(data)
        socketio.emit('score_update', data,namespace='/scoreboard', room=None, include_self=True)

    
    # instead of render the page, we should use redirect
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