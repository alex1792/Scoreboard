from flask import jsonify, request, current_app, send_file, Blueprint
import os
from .models import User, db
# from .blueprints import admin_bp
from .utils import check_authorization
from flask_jwt_extended import jwt_required, get_jwt_identity
from .extensions import socketio
from .utils import create_match_record, get_match_data
from .scheduler import generate_schedule, generate_schedule_for_tournament_from_matches
from .match_generator import generate_match
from .services.user_service import UserService
from .services.match_service import MatchService
from .services.schedule_service import TournamentScheduler
from .models import Tournament, ScheduleItem
from datetime import datetime


"""
This file contains the functions for the admin blueprint.

All the functions in this file require the user to be admin.
"""

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

"""
This function is used to update a user's role.

Role:
- admin
- host
- umpire
- user
"""
@admin_bp.route('/users', methods=['PUT'])
@jwt_required()
def update_user_role():
    try:
        authorization = check_authorization('admin')
        if authorization:
            return authorization

        data = request.get_json()
        user_id = data.get('user_id')
        new_role = data.get('new_role')

        if not user_id or not new_role:
            return jsonify({"status": "error", "message": "Missing user_id or new_role"}), 400

        user = UserService.update_user_role(user_id, new_role)

        socketio.emit('user_role_updated', {
            "username": user.username,
            "role": user.role
        }, namespace='/update_user_role')

        return jsonify({"status": "success", "data": user.serialize()}), 200
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        # print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to update user role"}), 500

"""
This function is used to get all the users in the database.
It will return all the users info to the frontend.
"""
@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    try:
        authorization = check_authorization('admin')
        if authorization:
            return authorization
        
        users_data = UserService.get_all_users()
        return jsonify({
            "status": "success",
            "data": users_data
        })
    except Exception as e:
        # print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to get users"}), 500

"""
This function is used to query all the users in database.
It will return all the users info to the frontend.
"""
@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def update_user_roles():
    try:
        authorization = check_authorization('admin')
        if authorization:
            return authorization
        
        data = request.get_json()
        username = data.get('username')
        role = data.get('role')

        user = UserService.update_user_role_by_username(username, role)
        
        # Socket.IO broadcast
        socketio.emit('user_role_updated', {
            "username": user.username if user else None,
            "role": user.role if user else None
        }, namespace='/user_role_update')

        return jsonify({
            "status": "success",
            "message": f"User {user.username if user else None} role updated to {role}"
        }), 200
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        # print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to update user role"}), 500

"""
This function is used to upload the match schedule. It will create the match record in the database.
However, it is using the fixed format, which is not flexible. It should be modified to addapted to the
current database structure.

IDEAS: by using the format based on the current database structure, the user can manually upload the match 
schedule so that the host can upload the schedule without using the sign-up function in the system.
"""
@admin_bp.route('/upload_match_schedule', methods=['POST'])
@jwt_required()
def upload_match_schedule():
    try:
        authorization = check_authorization('host')
        if authorization:
            return authorization
        
        file = request.files.get('file')
        if not file or not file.filename:
            return jsonify({"status": "error", "message": "No file provided"}), 400
        if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
            return jsonify({"status": "error", "message": "Invalid file format, only .csv and .xlsx are allowed"}), 400

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
            match_data = {
                'player1_name': player1,
                'player2_name': player2,
                'category': category,
                'status': 'Scheduled'
            }
            match = MatchService.create_match(match_data)
            created_matches.append(match)

        return jsonify({"status": "success", "message": "Matches created successfully", "matches": created_matches}), 200
    except Exception as e:
        # print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to upload match schedule"}), 500

"""
This function is used to generate the match schedule. It will generate the schedule based on the 
the priciple of minimizing the number of consecutive players. Which means that the scheduling algorithm
is trying to avoid players to play back to back.

However, for some of the matches, it can not satisfy the principle. So the function will try to minimize
the number of consecutive players.
"""
@admin_bp.route('/upload_all_matches', methods=['POST'])
@jwt_required()
def generate_match_schedule():
    try:
        auth = check_authorization('host')
        if auth:
            return auth
        
        file = request.files.get('file')
        total_court = request.form.get('total_court', 6)
        try:
            total_court = int(total_court)
        except (ValueError, TypeError):
            total_court = 6

        if not file or not file.filename:
            return jsonify({"status": "error", "message": "No file provided"}), 400
        if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
            return jsonify({"status": "error", "message": "Invalid file format, only .csv and .xlsx are allowed"}), 400

        import pandas as pd
        if file.filename.endswith('.csv'):
            f = pd.read_csv(file.stream, encoding='utf-8')
        else:
            f = pd.read_excel(file.stream, engine='openpyxl')

        instance_path = current_app.instance_path
        output_path = os.path.join(instance_path, 'round_robin_schedule.xlsx')
        
        generate_schedule(f, total_court, output_path)


        return send_file(output_path, as_attachment=True, download_name='round_robin_schedule.xlsx')
    except Exception as e:
        # print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Error creating match schedule"}), 500

"""
This function is used to generate all the possible matches. It will generate the matches based on
each event and group. For each event and group, it will be using the corresponding rules. For example,
for MS-A, if the parameter is 'r', the match will be generated based on the round-robin ruld. Likewise, 
for MS-B, if the parameter is 'e', the match will be generated based on the elimination rule.

However, the function is kinda fixed. It is not flexible. It is using the fixed format of the excel file.
It must be modified to addapted the current database structure. By using the current database structure,
the function can generate the matches based on the requirements.
"""
@admin_bp.route('/upload_participants', methods=['POST'])
@jwt_required()
def upload_participants():
    try:
        auth = check_authorization('host')
        if auth:
            return auth

        file = request.files.get('file')
        rules_string = request.form.get('rules', '')  # 獲取前端發送的規則字符串

        if not file or not file.filename:
            return jsonify({"status": "error", "message": "No file provided"}), 400
        if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
            return jsonify({"status": "error", "message": "Invalid file format, only .csv and .xlsx are allowed"}), 400

        # 解析規則字符串
        rules = {}
        if rules_string:
            rule_parts = rules_string.split(';')
            for part in rule_parts:
                if ':' in part:
                    key, rule_part = part.split(':', 1)
                    if ',' in rule_part:
                        rule_type, group_size = rule_part.split(',', 1)
                        rules[key] = [rule_type, int(group_size)]
                    else:
                        rules[key] = [rule_part]

        # 如果沒有規則，使用默認值
        if not rules:
            categories = ['MS', 'WS', 'MD', 'WD', 'XD']
            flights = ['A', 'B', 'C']
            for cat in categories:
                for fl in flights:
                    key = f"{cat}-{fl}"
                    rules[key] = ['e']  # 默認淘汰賽

        import pandas as pd
        if file.filename.endswith('.csv'):
            f = pd.read_csv(file.stream, encoding='utf-8')
        else:
            f = pd.read_excel(file.stream, engine='openpyxl')

        instance_path = current_app.instance_path
        os.makedirs(instance_path, exist_ok=True)
        output_path = os.path.join(instance_path, 'all_matches.xlsx')
        
        # 提取 categories 和 flights 用於 generate_match
        categories = list(set([key.split('-')[0] for key in rules.keys()]))
        flights = list(set([key.split('-')[1] for key in rules.keys()]))
        
        generate_match(f, categories, flights, rules, output_path)

        return send_file(output_path, as_attachment=True, download_name='all_matches.xlsx')
    except Exception as e:
        # print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Error creating match schedule"}), 500

@admin_bp.route('/<int:tournament_id>/generate_schedule_for_tournament', methods=['POST'])
@jwt_required()
def generate_schedule_for_tournament(tournament_id):
    """
    This function is used to generate the schedule for a tournament.
    All the match records are stored in the database, so it won't need to upload any file.
    Fully based on the database.
    """
    try:
        auth = check_authorization('host')
        if auth:
            return auth

        # 從 JSON 請求中獲取參數
        request_data = request.get_json() or {}
        total_court = request_data.get('total_court', 6)
        
        try:
            total_court = int(total_court)
        except (ValueError, TypeError):
            total_court = 6

        # 從資料庫獲取原始 Match 對象
        matches = MatchService.get_raw_matches_by_tournament(tournament_id)
        if not matches:
            return jsonify({
                "status": "error",
                "message": "No matches found for this tournament"
            }), 404

        # 創建輸出檔案路徑
        instance_path = current_app.instance_path
        os.makedirs(instance_path, exist_ok=True)
        output_filename = f"tournament_{tournament_id}_schedule.xlsx"
        output_path = os.path.join(instance_path, output_filename)
        
        # 生成賽程表
        # result = generate_schedule_for_tournament_from_matches(matches, total_court, output_path)

        scheduler = TournamentScheduler(total_court=total_court)
        scheduler.schedule_tournament(matches, tournament_id)
        scheduler._write_schedule(output_path)
        
        # 返回生成的賽程表檔案
        return send_file(
            output_path,
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
            
    except Exception as e:
        # print(f"Error generating schedule for tournament: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Error generating schedule: {str(e)}"
        }), 500

@admin_bp.route('/tournament/<int:tournament_id>/upload-schedule', methods=['POST'])
@jwt_required()
def upload_schedule(tournament_id):
    """上傳修改後的賽程表"""
    try:
        # print(f"Uploading schedule for tournament {tournament_id}")
        # 檢查檔案
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400
        
        file = request.files['file']
        
        # 建立 scheduler 實例並處理上傳
        scheduler = TournamentScheduler(1)  # total_court 暫時設為 1，因為這裡不需要
        result = scheduler.process_uploaded_schedule(file, tournament_id)
        
        # 根據結果返回適當的 HTTP 狀態碼
        if result['status'] == 'error':
            return jsonify(result), 400
        elif result['status'] == 'partial_success':
            return jsonify(result), 200
        else:
            return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Upload failed: {str(e)}'
        }), 500
    
# ------------- WebSocket events for user role updates ----------------
@socketio.on('connect', namespace='/user_role_update')
def handle_connect():
    print("[WebSocket] Client connected to /user_role_update namespace")

@socketio.on('disconnect', namespace='/user_role_update')
def handle_disconnect():
    print("[WebSocket] Client disconnected from /user_role_update namespace")
# ----------------------------------------------------------------------