# app/user.py (完整版)
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .services.user_service import UserService
from .utils import check_authorization
from .models import User

user_bp = Blueprint('user', __name__, url_prefix='/api/users')

@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    """獲取用戶列表"""
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

@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_by_id(user_id):
    """根據ID獲取用戶詳情"""
    try:
        user = UserService.get_user_by_id(user_id)
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
        
        user_data = {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "email": user.email
        }
        
        return jsonify({
            "status": "success",
            "data": user_data
        })
    except Exception as e:
        # print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to get user"}), 500

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_current_user_profile():
    """獲取當前用戶資料"""
    try:
        current_user_id = get_jwt_identity()
        user = UserService.get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
        
        user_data = {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "email": user.email
        }
        
        return jsonify({
            "status": "success",
            "data": user_data
        })
    except Exception as e:
        # print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to get user profile"}), 500

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_current_user_profile():
    """更新當前用戶資料"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        user = UserService.get_user_by_id(current_user_id)
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
        
        # 更新允許的欄位
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            user.email = data['email']
        
        from .models import db
        db.session.commit()
        
        user_data = {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "email": user.email
        }
        
        return jsonify({
            "status": "success",
            "message": "Profile updated successfully",
            "data": user_data
        })
    except Exception as e:
        # print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to update profile"}), 500

@user_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """更新用戶資料 (管理員功能)"""
    try:
        authorization = check_authorization('admin')
        if authorization:
            return authorization
        
        data = request.get_json()
        user = UserService.get_user_by_id(user_id)
        
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
        
        # 更新允許的欄位
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            user.email = data['email']
        if 'role' in data:
            user.role = data['role']
        
        from .models import db
        db.session.commit()
        
        user_data = {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "email": user.email
        }
        
        return jsonify({
            "status": "success",
            "message": "User updated successfully",
            "data": user_data
        })
    except Exception as e:
        # print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to update user"}), 500

@user_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """刪除用戶 (管理員功能)"""
    try:
        authorization = check_authorization('admin')
        if authorization:
            return authorization
        
        user = UserService.get_user_by_id(user_id)
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
        
        from .models import db
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": f"User {user.username} deleted successfully"
        })
    except Exception as e:
        # print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to delete user"}), 500

@user_bp.route('/search', methods=['GET'])
@jwt_required()
def search_users():
    """搜尋用戶"""
    try:
        authorization = check_authorization('guest')
        if authorization:
            return authorization
        
        query = request.args.get('q', '')
        role = request.args.get('role', '')
        
        # 建立搜尋條件
        search_filters = []
        if query:
            search_filters.append(
                (User.first_name.contains(query) | 
                 User.last_name.contains(query) | 
                 User.username.contains(query))
            )
        if role:
            search_filters.append(User.role == role)
        
        # 執行搜尋
        from .models import db
        users = User.query.filter(*search_filters).all()
        
        users_data = []
        for user in users:
            user_data = {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "email": user.email
            }
            users_data.append(user_data)
        
        return jsonify({
            "status": "success",
            "data": users_data
        })
    except Exception as e:
        # print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to search users"}), 500

@user_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """獲取用戶統計資料"""
    try:
        authorization = check_authorization('host')
        if authorization:
            return authorization
        
        from .models import db
        
        # 統計各角色用戶數量
        role_stats = db.session.query(
            User.role, 
            db.func.count(User.id)
        ).group_by(User.role).all()
        
        total_users = User.query.count()
        
        stats = {
            "total_users": total_users,
            "role_distribution": {role: count for role, count in role_stats}
        }
        
        return jsonify({
            "status": "success",
            "data": stats
        })
    except Exception as e:
        # print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Failed to get user stats"}), 500