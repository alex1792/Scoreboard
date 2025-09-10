from flask import jsonify, Blueprint
from .models import Tournament, Format, Event, Group, Match, User
from .models import db
from .utils import check_authorization
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from datetime import datetime
from .services.tournament_service import TournamentService
from .services.match_service import MatchService
from .services.schedule_service import TournamentScheduler
"""
This file contains the functions for the tournament blueprint. 
"""

tournament_bp = Blueprint('tournament', __name__, url_prefix='/api/tournaments')

"""
This function is  used to get all tournaments information in the database.
It will return all the tournaments info to the frontend. Then the frontend
will display all the tournaments in the /tournaments page.
"""
@tournament_bp.route('/', methods=['GET'])
def get_tournaments():
    """get all tournaments info from tournament_service"""
    try:
        tournaments_data = TournamentService.get_all_tournaments()
        if not tournaments_data:
            return jsonify({"status": "error", "message": "No tournaments found"}), 404
        
        return jsonify({
            "status": "success", 
            "message": "Tournaments fetched successfully", 
            "data": tournaments_data
        }), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to get tournaments"}), 500

"""
This function is  used to get the details of a specific tournament. Search by tournament_id.
It will return the details of the tournament, including the id, name, start_date, end_date, 
location, status, events. This info will be uesed to show the tournamet details in the /tournaments/<int:tournament_id> page.
"""
@tournament_bp.route('/<int:tournament_id>', methods=['GET'])
def get_tournament_details(tournament_id):
    """get tournament details from tournament_service"""
    try:
        tournament_data = TournamentService.get_tournament_by_id(tournament_id)
        if not tournament_data:
            return jsonify({"status": "error", "message": "Tournament not found"}), 404
        
        return jsonify({
            "status": "success", 
            "message": "Tournament details fetched successfully", 
            "data": tournament_data
        }), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to get tournament details"}), 500


"""
This function is used to create a new tournament. It will create a new tournament record in the database.
"""
@tournament_bp.route('/create_tournament', methods=['POST'])
@jwt_required()
def create_tournament():
    """create tournament from tournament_service"""
    try:
        auth = check_authorization('host')
        if auth:
            return auth
    except Exception as e:
        return jsonify({"status": "error", "message": "Please Login to create a tournament"}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No tournament data provided"}), 400

        tournament_info = data.get('tournament')
        events_info = data.get('events')

        # get current user id
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({"status": "error", "message": "Please Login to create a tournament"}), 401

        # add host_id to tournament_info
        tournament_info['host_id'] = current_user_id

        if not tournament_info or not events_info:
            return jsonify({"status": "error", "message": "Missing tournament or events data"}), 400
        
        tournament = TournamentService.create_tournament(tournament_info, events_info)
        return jsonify({"status": "success", "message": "Tournament created successfully"}), 200
        
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Error creating tournament"}), 500

"""
This function is used to generate matches by registration records.
"""
@tournament_bp.route('/<int:tournament_id>/generate_matches', methods=['POST'])
@jwt_required()
def generate_matches_by_registration(tournament_id):
    """generate matches by registration records from tournament_service"""
    print('generate_matches_by_registration')
    try:
        auth = check_authorization('host')
        if auth:
            return auth
    except Exception as e:
        return jsonify({"status": "error", "message": "Please Login to generate matches"}), 500
    
    try:
        matches = TournamentService.generate_matches_by_registration(tournament_id)
        matches_data = []
        for match in matches:
            match_data = {
                'id': match.id,
                'tournament_id': match.tournament_id,
                'event_id': match.event_id,
                'group_id': match.group_id,
                'event_type': match.event_type,
                'player1_id': match.player1_id,
                'player2_id': match.player2_id,
                'team1_player1_id': match.team1_player1_id,
                'team1_player2_id': match.team1_player2_id,
                'team2_player1_id': match.team2_player1_id,
                'team2_player2_id': match.team2_player2_id,
                'player1_score': match.player1_score,
                'player2_score': match.player2_score,
                'status': match.status,
                'umpire_id': match.umpire_id
            }
            matches_data.append(match_data)
        
        return jsonify({"status": "success", "message": "Matches generated successfully", "data": matches_data}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to generate matches"}), 500

"""
This function is used to get all matches by tournament_id.
It will return all the matches info to the frontend. Then the frontend
will display all the matches in the /tournaments/<int:tournament_id>/matches page.
"""
@tournament_bp.route('/<int:tournament_id>/matches', methods=['GET'])
def get_matches_by_tournament(tournament_id):
    """get matches by tournament_id from match_service"""
    try:
        matches = MatchService.get_matches_by_tournament(tournament_id)
        if not matches:
            print("No matches found")
            return jsonify({"status": "error", "message": "No matches found"}), 404
        # print(matches)
        return jsonify({"status": "success", "message": "Matches fetched successfully", "data": matches}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to get matches"}), 500

"""
This function is used to get the tournament schedule.
"""
@tournament_bp.route('/<int:tournament_id>/schedule', methods=['GET'])
def get_tournament_schedule(tournament_id):
    """Return the tournament schedule from tournament service"""
    try:
        schedule_data = TournamentService.get_schedule_by_tournament(tournament_id)
        if not schedule_data:
            return jsonify({'status': 'error', 'message': 'No schedule data found'}), 404
        
        return jsonify({
            'status': 'success',
            'schedule': schedule_data
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

"""
This function is used to delete all matches of a specific tournament
"""
@tournament_bp.route('/<int:tournament_id>/delete_all_matches', methods=['POST'])
@jwt_required()
def delete_all_matches(tournament_id):
    try:
        # check authorization
        try:
            auth = check_authorization('host')
            if auth:
                return auth
        except Exception as e:
            return jsonify({"status": "error", "message": "Please Login to generate matches"}), 500


        # delete matches in particular tournament
        MatchService.delete_all_matches_by_tournament_id(tournament_id)

        return jsonify({'status': 'success', 'message': f'All matches with tournament_id = {tournament_id} are deleted'}), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@tournament_bp.route('/<int:tournament_id>/delete_tournament', methods=['POST'])
@jwt_required()
def delete_tournament(tournament_id):
    try:
        auth = check_authorization('host')
        if auth:
            return auth
        
        ret = TournamentService.delete_tournament(tournament_id)
        if not ret:
            return jsonify({'status': 'error', 'message': f'Tournament with tournament_id = {tournament_id} is not found'}), 404
        return jsonify({'status': 'success', 'message': f'Tournament with tournament_id = {tournament_id} is deleted'}), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": "Please Login to delete a tournament"}), 500

@tournament_bp.route('/<int:tournament_id>/bracket', methods=['GET'])
def get_tournament_bracket(tournament_id):
    print('get_tournament_bracket')
    try:
        matches = Match.query.filter_by(tournament_id=tournament_id).all()
        
        print(f"Total matches found: {len(matches)}")
        for match in matches:
            print(f"Processing match {match.id}: Round {match.round}, Match {match.match_number}")
        
        match_data = []
        for match in matches:
            # 獲取格式信息
            event = Event.query.get(match.event_id)
            group = Group.query.get(match.group_id)
            format_info = Format.query.get(group.format_id) if group else None
            
            # 處理玩家名稱 - 支持單打和雙打
            player1_name = 'TBD'
            player2_name = 'TBD'
            
            # 如果是雙打比賽（MD, WD, XD），組合隊友名稱
            if match.event_type in ['MD', 'WD', 'XD']:
                # 檢查是否有雙打隊友信息
                if match.team1_player1_name and match.team1_player2_name:
                    player1_name = f"{match.team1_player1_name} / {match.team1_player2_name}"
                elif match.player1_name:
                    player1_name = match.player1_name
                else:
                    player1_name = 'TBD'
                
                if match.team2_player1_name and match.team2_player2_name:
                    player2_name = f"{match.team2_player1_name} / {match.team2_player2_name}"
                elif match.player2_name:
                    player2_name = match.player2_name
                else:
                    player2_name = 'TBD'
            else:
                # 單打比賽
                player1_name = match.player1_name or 'TBD'
                player2_name = match.player2_name or 'TBD'
            
            # 處理勝者名稱
            winner_name = match.winner_name
            if not winner_name and match.status == 'Finished':
                # 如果沒有 winner_name 但有勝者 ID，嘗試構建勝者名稱
                if match.event_type in ['MD', 'WD', 'XD']:
                    if match.winner1_id and match.winner2_id:
                        winner1 = User.query.get(match.winner1_id)
                        winner2 = User.query.get(match.winner2_id)
                        if winner1 and winner2:
                            winner_name = f"{winner1.get_full_name()} / {winner2.get_full_name()}"
                else:
                    if match.winner1_id:
                        winner1 = User.query.get(match.winner1_id)
                        if winner1:
                            winner_name = winner1.get_full_name()
            
            # 計算比賽在 bracket 中的位置
            print(f"Calculating position for match {match.id} (Round {match.round}, Match {match.match_number})")
            bracket_position = calculate_bracket_position(match)
            
            connections = get_connection_info(match)

            match_data.append({
                'id': match.id,
                'event_id': match.event_id,
                'group_id': match.group_id,
                'category': event.name if event else '',
                'group': group.name if group else '',
                'format_type': format_info.type if format_info else 'elimination',
                'round': match.round,
                'match_number': match.match_number,
                'player1': player1_name,
                'player2': player2_name,
                'winner': winner_name,
                'status': match.status,
                'score1': match.player1_score,
                'score2': match.player2_score,
                # 添加缺失的字段
                'player1_game_won': match.player1_game_won,
                'player2_game_won': match.player2_game_won,
                'game1_score1': match.game1_score1,
                'game1_score2': match.game1_score2,
                'game2_score1': match.game2_score1,
                'game2_score2': match.game2_score2,
                'game3_score1': match.game3_score1,
                'game3_score2': match.game3_score2,
                'current_game': match.current_game,
                'umpire_id': match.umpire_id,
                'next_match_id': match.next_match_id,
                'prev_match1_id': match.prev_match1_id,
                'prev_match2_id': match.prev_match2_id,
                'event_type': match.event_type,
                'bracket_position': bracket_position,
                'connections': connections
            })
        
        print(f"Found {len(match_data)} matches for tournament {tournament_id}")
        return jsonify({
            'status': 'success',
            'matches': match_data
        })
        
    except Exception as e:
        print(f"Error in get_tournament_bracket: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def calculate_bracket_position(match):
    """計算比賽在 bracket 中的位置 - 金字塔形樹狀圖"""
    if not match.round or not match.match_number:
        return 0
    
    # 縮短間距常量
    MATCH_HEIGHT = 120  # match box 高度
    MATCH_SPACING = 120  # match box 之間的間距
    TOTAL_MATCH_SPACE = MATCH_HEIGHT + MATCH_SPACING  # 總間距 = 240px
    
    if match.round == 1:
        # 第一輪：均勻分布
        match_index = match.match_number - 1
        return match_index * TOTAL_MATCH_SPACE
    elif match.round == 2:
        # 第二輪：位於第一輪兩個比賽的中間
        match_index = match.match_number - 1
        prev_match1_index = match_index * 2
        prev_match2_index = prev_match1_index + 1
        
        prev_match1_position = prev_match1_index * TOTAL_MATCH_SPACE
        prev_match2_position = prev_match2_index * TOTAL_MATCH_SPACE
        
        return (prev_match1_position + prev_match2_position) / 2
    elif match.round == 3:
        # 第三輪：位於第二輪兩個比賽的中間
        # 第二輪的位置是 120px 和 600px
        return (120 + 600) / 2  # = 360px
    
    return 0

def get_connection_info(match):
    """獲取比賽的連接線信息"""
    if not match.round or not match.match_number:
        return None
    
    # 獲取下一輪的比賽
    next_round_matches = Match.query.filter_by(
        tournament_id=match.tournament_id,
        event_id=match.event_id,
        group_id=match.group_id,
        round=match.round + 1
    ).order_by(Match.match_number).all()
    
    # 如果沒有下一輪，就沒有連接線
    if not next_round_matches:
        return None
    
    # 計算這個比賽會連接到下一輪的哪個比賽
    next_match_number = (match.match_number - 1) // 2 + 1
    
    # 找到對應的下一輪比賽
    next_match = None
    for nm in next_round_matches:
        if nm.match_number == next_match_number:
            next_match = nm
            break
    
    if not next_match:
        return None
    
    # 檢查下一輪的這個比賽是否只有一個前輪比賽指向它
    prev_round_matches = Match.query.filter_by(
        tournament_id=match.tournament_id,
        event_id=match.event_id,
        group_id=match.group_id,
        round=match.round
    ).order_by(Match.match_number).all()
    
    # 計算指向這個下一輪比賽的前輪比賽數量
    pointing_matches = []
    for pm in prev_round_matches:
        pm_next_match_number = (pm.match_number - 1) // 2 + 1
        if pm_next_match_number == next_match_number:
            pointing_matches.append(pm)
    
    # 如果只有一個前輪比賽指向這個下一輪比賽，使用 'center' 位置
    if len(pointing_matches) == 1:
        position = 'center'
    else:
        # 否則使用 top/bottom 區分
        position = 'top' if match.match_number % 2 == 1 else 'bottom'
    
    # 添加調試信息
    print(f"Match {match.id} (Round {match.round}, Match {match.match_number}) -> Next Match {next_match.id} (Round {next_match.round}, Match {next_match.match_number}) with position {position}")
    
    return [{
        'match_id': next_match.id,
        'position': position
    }]

@tournament_bp.route('/<int:tournament_id>/player-history', methods=['POST'])
def get_player_history(tournament_id):
    """query history of a player"""
    try:
        data = request.get_json()
        player_name = data.get('player_name')
        
        if not player_name:
            return jsonify({
                'status': 'error',
                'message': 'Player name is required'
            }), 400
        
        # use tournament_service to get the player history
        result = TournamentService.query_players_history(player_name, tournament_id)
        
        # 如果 TournamentService 返回成功，直接返回其 data 部分
        if result.get('status') == 'success':
            return jsonify({
                'status': 'success',
                'data': result.get('data')  # 只返回內層的 data
            })
        else:
            return jsonify(result)  # 返回錯誤信息
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }), 500