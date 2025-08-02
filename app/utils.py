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
        # 單打處理
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
            
        # 處理單打淘汰賽晉級比賽 - 修正邏輯
        if match.prev_match1_id is not None:
            # 只有在 player1_name 還是 "Winner of Match" 格式時才重新生成
            if not match.player1_name or 'Winner of Match' in player1:
                if 'Winner of Match' in player1:
                    player1 = player1  # 保持原樣
                else:
                    player1 = f"Winner of Match #{match.prev_match1_id}"
            
            if not match.player2_name or 'Winner of Match' in player2:
                if 'Winner of Match' in player2:
                    player2 = player2  # 保持原樣
                else:
                    player2 = f"Winner of Match #{match.prev_match2_id}"
                
    else: 
        # 雙打處理
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
        
        # 統一處理雙打選手顯示邏輯 - 修正邏輯
        if match.prev_match1_id is not None:
            # 淘汰賽晉級比賽
            if not match.team1_player1_name or 'Winner of Match' in team1_player1:
                if 'Winner of Match' in team1_player1:
                    player1 = team1_player1  # 保持原樣
                else:
                    player1 = f"Winner of Match #{match.prev_match1_id}"
            else:
                # 使用已更新的名稱
                if team1_player1 and team1_player2 and team1_player1 != "N/A" and team1_player2 != "N/A":
                    player1 = f"{team1_player1} / {team1_player2}"
                else:
                    player1 = team1_player1 or team1_player2 or "TBD"
            
            if not match.team2_player1_name or 'Winner of Match' in team2_player1:
                if 'Winner of Match' in team2_player1:
                    player2 = team2_player1  # 保持原樣
                else:
                    player2 = f"Winner of Match #{match.prev_match2_id}"
            else:
                # 使用已更新的名稱
                if team2_player1 and team2_player2 and team2_player1 != "N/A" and team2_player2 != "N/A":
                    player2 = f"{team2_player1} / {team2_player2}"
                else:
                    player2 = team2_player1 or team2_player2 or "TBD"
        else:
            # 第一輪比賽（Round Robin 或 Elimination 第一輪）
            if team1_player1 and team1_player2 and team1_player1 != "N/A" and team1_player2 != "N/A":
                player1 = f"{team1_player1} / {team1_player2}"
            else:
                player1 = team1_player1 or team1_player2 or "TBD"
            
            if team2_player1 and team2_player2 and team2_player1 != "N/A" and team2_player2 != "N/A":
                player2 = f"{team2_player1} / {team2_player2}"
            else:
                player2 = team2_player1 or team2_player2 or "TBD"

    # 獲取相關對象
    event = Event.query.get(match.event_id)
    group = Group.query.get(match.group_id)
    
    # 修正 umpire 查詢，避免 None 主鍵警告
    umpire = None
    if match.umpire_id is not None:
        umpire = User.query.get(match.umpire_id)

    match_data = {
        "id": match.id,
        "category": event.category if event else "Unknown",
        "group": group.name if group else "Unknown",
        "player1": player1,
        "player2": player2,
        "score1": match.player1_score,
        "score2": match.player2_score,
        "status": match.status,
        "umpire": umpire.get_full_name() if umpire else "N/A",
        "umpire_id": match.umpire_id,
        "current_game": match.current_game,
        "player1_game_won": match.player1_game_won,
        "player2_game_won": match.player2_game_won, 
        "game1_score1": match.game1_score1,
        "game1_score2": match.game1_score2,
        "game2_score1": match.game2_score1,
        "game2_score2": match.game2_score2,
        "game3_score1": match.game3_score1,
        "game3_score2": match.game3_score2,
        "current_game": match.current_game,
        "player1_game_won": match.player1_game_won,
        "player2_game_won": match.player2_game_won
    }

    # check if the match is elimination match
    if hasattr(match, 'round') and match.round is not None and hasattr(match, 'match_number') and match.match_number is not None:
        match_data.update({
            "round": match.round,
            "match_number": match.match_number,
            "prev_match1_id": match.prev_match1_id,
            "prev_match2_id": match.prev_match2_id,
            "next_match_id": match.next_match_id,
            "player1_from_match": match.player1_from_match,
            "player2_from_match": match.player2_from_match
        })
    
    # 添加勝者信息
    if match.status == 'Finished':
        # 優先使用 winner_name 和 loser_name（用於文件上傳註冊）
        if match.winner_name and match.loser_name:
            winner_name = match.winner_name
            loser_name = match.loser_name
        else:
            # 從 User 關係獲取（用於 User-based registrations）
            if match.event_type in ['MS', 'WS']:  # 單打
                winner_name = match.winner1.get_full_name() if match.winner1 else 'Unknown'
                loser_name = match.loser1.get_full_name() if match.loser1 else 'Unknown'
            else:  # 雙打
                winner1_name = match.winner1.get_full_name() if match.winner1 else 'Unknown'
                winner2_name = match.winner2.get_full_name() if match.winner2 else 'Unknown'
                loser1_name = match.loser1.get_full_name() if match.loser1 else 'Unknown'
                loser2_name = match.loser2.get_full_name() if match.loser2 else 'Unknown'
                
                winner_name = f"{winner1_name} / {winner2_name}"
                loser_name = f"{loser1_name} / {loser2_name}"
        
        match_data['winner'] = winner_name
        match_data['loser'] = loser_name
        match_data['winner1_id'] = match.winner1_id
        match_data['winner2_id'] = match.winner2_id
        match_data['loser1_id'] = match.loser1_id
        match_data['loser2_id'] = match.loser2_id
    
    return match_data

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
- guest(not logged in): can access check all tournaments, check tournament match scores
"""
def check_authorization(required_role='admin'):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    if not current_user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    # define the permission hierachy (higher role = higher permission)
    role_hierachy = {
        'admin': 4,
        'host': 3,
        'umpire': 2,
        'user': 1,
        'guest': 0
    }

    current_user_role_level = role_hierachy[current_user.role]
    required_role_level = role_hierachy[required_role]
    
    # check if current user role has the permission to access the feature
    if current_user_role_level < required_role_level:
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