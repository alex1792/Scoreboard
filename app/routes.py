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
from .models import Match, db, User

app = Flask(__name__)
app.config['DATABASE'] = 'database.db'


@home_blueprint.route('/')
def home():
    return render_template('scoreboard/home.html')


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


@users_blueprint.route('/users')
def query_users():
    users = User.query.all()
    return render_template('scoreboard/users.html', users=users)


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


@match_blueprint.route('/match')
def query_matches():
    matches = Match.query.all()
    return render_template('scoreboard/matches.html', matches=matches)


@create_match_blueprint.route('/create_match', methods=['POST', 'GET'])
def create_match():
    if request.method == 'POST':
        player1_username = request.form['player1_username']
        player2_username = request.form['player2_username']
        player1 = User.query.filter_by(username=player1_username).first()
        player2 = User.query.filter_by(username=player2_username).first()
        status = 'Scheduled'
        if player1 and player2:
            new_match = Match(player1_id=player1.id, player2_id=player2.id, status=status)
            db.session.add(new_match)
            db.session.commit()
        return redirect(url_for('create_match_blueprint.create_match'))
    else:
        return render_template('scoreboard/create_match.html')


@clear_all_match_blueprint.route('/clear_match', methods=['POST'])
def clear_all_match():
    Match.query.delete()
    db.session.commit()
    return redirect(url_for('manage_match_blueprint.manage_match'))


@assign_umpire_blueprint.route('/assign_umpire')
def assign_umpire():
    matches = Match.query.all()
    return render_template('scoreboard/assign_umpire.html', matches=matches)

@assign_umpire_blueprint.route('/assign_umpire/<int:match_id>', methods=['POST'])
def set_umpire(match_id):
    umpire_id = request.form.get('umpire_id')
    match = Match.query.get(match_id)
    umpire = User.query.get(umpire_id)
    if match and umpire:
        match.umpire_id = umpire.id
        db.session.commit()
        data = {
            'match_id': str(match.id),
            'score1': match.score1,
            'score2': match.score2,
            'match_status': match.status,
            'umpire_name': umpire.username
        }
        socketio.emit('match_update', data, namespace='/scoreboard', room=None, include_self=True)
        return jsonify({'success': True}), 200
    return jsonify({'success': False, 'message': 'Match or umpire not found'}), 400
