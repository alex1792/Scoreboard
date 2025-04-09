import functools
import sqlite3
from flask import Flask, render_template, redirect, url_for, request
from flask_login import current_user, login_required
from .blueprints import (home_blueprint, scoreboard_blueprint, umpire_blueprint, 
                         admin_blueprint, users_blueprint, match_blueprint, 
                         manage_match_blueprint, create_match_blueprint, clear_all_match_blueprint,
                         change_match_status_blueprint)
from .db import Database
from .form import ScoreForm
from .extensions import socketio

app = Flask(__name__)
app.config['DATABASE'] = 'database.db'

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
    db.close()
    
    if match_info:
        match_id = match_info['match_id']
        player1_name = match_info['player1_name']
        player2_name = match_info['player2_name']
        score1 = match_info['score1']
        score2 = match_info['score2']
        status = match_info['status']
        return render_template('scoreboard/scoreboard.html', player1_name=player1_name, player2_name=player2_name, score1=score1, score2=score2, match_id=match_id, match_status=status)
    else:
        return "No match found."
    
@scoreboard_blueprint.route('/update_score', methods=['POST'])
@login_required
def update_score():
    player = request.form.get('player') # player belongs to the set {Player1, Player2}
    score = int(request.form.get('score'))
    # print(player)
    
    db_name = 'database.db'
    db = Database(db_name)
    match_info = db.get_match_info()
    

    if match_info:        
        if player == 'Player1':
            player1_id = match_info['player1_id']
            db.update_score(player1_id, match_info, score)
        else:
            player2_id = match_info['player2_id']
            db.update_score(player2_id, match_info, score)
        
        # broadcast updated score to all clients viewing the this match
        match_info = db.get_match_info()
        data = {'match_id': str(match_info['match_id']), 'score1': match_info['score1'], 'score2': match_info['score2']}
        # print(data)
        socketio.emit('score_update', data,namespace='/scoreboard', room=None, include_self=True)

    # close database connection
    db.close()

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


@admin_blueprint.route('/admin', methods=['POST', 'GET'])
def set_umpire():
    if request.method == 'POST':
        username = request.form['username']
        is_judge = request.form['is_judge'] == 'true'
        
        # connect to database and update the user is_judge status
        db = Database('database.db')
        db.set_umpire(username, is_judge)
        db.close()
        
        # broadcast to the user so the stataus is now changed
        data = {'username':username, 'is_judge':is_judge}
        socketio.emit('user_role_updated', data, namespace='/admin', room=None, include_self=True)
        
        # redirect to home
        return redirect(url_for('home_blueprint.home'))
    else:
        return render_template('scoreboard/admin.html')
    
@socketio.on('connect', namespace='/admin')
def admin_connect():
    print("User is connected to /admin namespace")

@users_blueprint.route('/users')
def query_users():
    db = Database('database.db')
    all_users = db.get_all_users()
    db.close()
    return render_template('scoreboard/users.html', users=all_users)

@manage_match_blueprint.route('/manage_match', methods=['POST', 'GET'])
def manage_match():
    db = Database('database.db')
    
    if request.method == 'POST':
        match_id = request.form['match_id']
        db.clear_match_by_id(match_id)
        db.close()
        return redirect(url_for('match_blueprint.query_matches'))  # 重定向到 GET, follow PRG mode (POST/REDIRECT/GET)

    else:
        db.close()
        return render_template('scoreboard/manage_match.html')


@match_blueprint.route('/match')
def query_matches():
    db = Database('database.db')
    all_matches = db.get_all_match()
    db.close()
    return render_template('scoreboard/matches.html', matches=all_matches)

@create_match_blueprint.route('/create_match', methods=['POST', 'GET'])
def create_match():
    if request.method == 'POST':
        player1_username = request.form['player1_username']
        player2_username = request.form['player2_username']

        # query ids of player1 and player2
        db = Database('database.db')
        player1_id = db.get_user_id_by_username(player1_username)
        player2_id = db.get_user_id_by_username(player2_username)

        # add match
        db.add_match(player1_id, player2_id)
        db.close()
        return redirect(url_for('create_match_blueprint.create_match'))
    else:
        return render_template('scoreboard/create_match.html')
    
@clear_all_match_blueprint.route('/clear_match', methods=['POST'])
def clear_all_match():
    db = Database('database.db')
    db.clear_all_match()
    db.close()
    return redirect(url_for('manage_match_blueprint.manage_match'))

@change_match_status_blueprint.route('/change_match_status', methods=['POST'])
def change_match_status():
    new_status = request.form['new_status']
    match_id = request.form['match_id']
    db = Database('database.db')
    db.change_match_status(new_status, match_id)
    db.close()

    # broadcast
    socketio.emit('match_status_update', {'match_id': str(match_id), 'match_status': new_status}, namespace='/scoreboard', include_self=True)

    return redirect(url_for('scoreboard_blueprint.index', match_id=match_id))

    

