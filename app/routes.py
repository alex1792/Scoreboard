import functools

from flask import render_template, redirect, url_for
from flask_login import current_user
from .blueprints import home_blueprint, scoreboard_blueprint, umpire_blueprint
from .db import Database
from .form import ScoreForm


@home_blueprint.route('/')
def home():
    if current_user.is_authenticated:
        return render_template('scoreboard/home.html', editable=True)
    else:
        return render_template('scoreboard/home.html', editable=False)


@scoreboard_blueprint.route('/scoreboard')
def index():
    db_name = 'database.db'
    db = Database(db_name)
    match_info = db.get_match_info()
    db.close()  # 關閉資料庫連接
    
    # match_info = Database.get_match_info()
    if match_info:
        player1_name = match_info['player1_name']
        player2_name = match_info['player2_name']
        score1 = match_info['score1']
        score2 = match_info['score2']
        return render_template('scoreboard/scoreboard.html', player1_name=player1_name, player2_name=player2_name, score1=score1, score2=score2)
    else:
        return "No match found."
    
# @umpire_blueprint.route('umpire', methods=['GET', 'POST'])
# @login_required
# def umpire():
#     if not current_user.is_judge:
#         return redirect(url_for('routes_app.homepage'))
    
    # form  = Scoreform()