from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from .models import User, Event, Registration, Match, db, Group

"""
This file contains the utility functions for the app. The funcitons in this
file are used in the routes.py file. These functions are just general functions,
not related to any specific blueprint or route.

The original route.py will be rewritten into multiple files. Each file will be
related to aspecific blueprint. In this way, the code will be more organized, and easier
to maintain. You can test each blueprint respectively. This is the benefit of using such 
file structure.
"""

def get_match_data(match):
    if match.event_type in ['MS', 'WS']: 
        # 優先使用存儲的姓名，如果沒有則嘗試從 User 表獲取
        if match.player1_name:
            player1 = match.player1_name
        else:
            user1 = User.query.get(match.player1_id) if match.player1_id else None
            player1 = user1.get_full_name() if user1 else "N/A"
            
        if match.player2_name:
            player2 = match.player2_name
        else:
            user2 = User.query.get(match.player2_id) if match.player2_id else None
            player2 = user2.get_full_name() if user2 else "N/A"
    else: 
        # 雙打：優先使用存儲的姓名
        if match.team1_player1_name:
            team1_player1 = match.team1_player1_name
        else:
            user1 = User.query.get(match.team1_player1_id) if match.team1_player1_id else None
            team1_player1 = user1.get_full_name() if user1 else "N/A"
            
        if match.team1_player2_name:
            team1_player2 = match.team1_player2_name
        else:
            user2 = User.query.get(match.team1_player2_id) if match.team1_player2_id else None
            team1_player2 = user2.get_full_name() if user2 else "N/A"
            
        if match.team2_player1_name:
            team2_player1 = match.team2_player1_name
        else:
            user3 = User.query.get(match.team2_player1_id) if match.team2_player1_id else None
            team2_player1 = user3.get_full_name() if user3 else "N/A"
            
        if match.team2_player2_name:
            team2_player2 = match.team2_player2_name
        else:
            user4 = User.query.get(match.team2_player2_id) if match.team2_player2_id else None
            team2_player2 = user4.get_full_name() if user4 else "N/A"
        
        player1 = f"{team1_player1} & {team1_player2}"
        player2 = f"{team2_player1} & {team2_player2}"

    # 獲取相關對象
    event = Event.query.get(match.event_id)
    group = Group.query.get(match.group_id)
    
    # 修正 umpire 查詢，避免 None 主鍵警告
    umpire = None
    if match.umpire_id is not None:
        umpire = User.query.get(match.umpire_id)
    
    return {
        "id": match.id,
        "category": event.category if event else "Unknown",
        "group": group.name if group else "Unknown",
        "player1": player1,
        "player2": player2,
        "score1": match.player1_score,
        "score2": match.player2_score,
        "status": match.status,
        "umpire": umpire.get_full_name() if umpire else "N/A",
        "umpire_id": match.umpire_id
    }

"""
This function is used to check if the user is authorized to access the feature function.
The role parameter is used to check if the user is admin or user. In this project, there
are four roles: admin, host, umpire, user. Each role has different permissions.

For example, if you called check_authorization('user'), it will check if the current user 
is admin or user. If not, it will return the jsonify error message. Which meas the user does
not have the permission to access this feature.

Permisions:
- admin: can access all features
- host: can access create tournament, check registration, check match
- umpire: can access update match score
- user: can access sign-up tournament, check match, check all tournaments
- guest: can access check all tournaments, check tournament match scores
"""
def check_authorization(role='admin'):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # check if not admin, return error
    if not current_user or (current_user.role != 'admin' and current_user.role != role):
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    return None

"""
This function is used to get the user by the first name and last name.
It will return the User object if found, otherwise return None.
"""
def get_user_by_name(first_name, last_name):
    user = User.query.filter_by(first_name=first_name, last_name=last_name).first()
    if not user:
        print(f"User {first_name} {last_name} not found")
        return None
    return user

"""
This function is used to check if the user has already registered for the tournament (particular event and group).
If the user has already registered for the tournament, it will return True.
"""
def check_repeated_registration(tournament_id, user_id, event_id, group_id):
    registration = Registration.query.filter_by(tournament_id=tournament_id, user_id=user_id, event_id=event_id, group_id=group_id).first()
    if registration:
        return True
    return False

"""
This function is used to create a new match record in the database.
"""
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