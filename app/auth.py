from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from .extensions import db
from .models import User
import datetime  # 用於設定 JWT 過期時間

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')  # 加上 /api 前綴

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')

    # 驗證必要欄位
    if not username or not password or not first_name or not last_name:
        return jsonify({
            "status": "error",
            "message": "Username, password, first name, and last name are required."
        }), 400

    # 檢查用戶名是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({
            "status": "error",
            "message": "Username already exists."
        }), 409

    # 檢查 email 是否已存在（如果提供了 email）
    if email and User.query.filter_by(email=email).first():
        return jsonify({
            "status": "error",
            "message": "Email already exists."
        }), 409

    try:
        new_user = User()
        new_user.username = username
        new_user.password = generate_password_hash(password)
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.email = email if email else None
        new_user.role = 'user'
        db.session.add(new_user)
        db.session.commit()
        db.session.flush()

        # 生成 JWT Token（有效期 7 天）
        print('產生 token 時 identity: ', new_user.id, type(new_user.id))
        access_token = create_access_token(
            identity=str(new_user.id),
            expires_delta=datetime.timedelta(days=7)
        )

        return jsonify({
            "status": "success",
            "message": "User registered successfully.",
            "data": {
                "user": {
                    "id": new_user.id,
                    "username": new_user.username,
                    "first_name": new_user.first_name,
                    "last_name": new_user.last_name,
                    "email": new_user.email,
                    "role": new_user.role
                },
                "access_token": access_token
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {e}")  # 添加錯誤日誌
        return jsonify({
            "status": "error",
            "message": "Registration failed."
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    # get username and password from frontend
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # search user in database by username
    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({
            "status": "error",
            "message": "Invalid username or password."
        }), 401

    # generate JWT Token（valid in 7 days）
    access_token = create_access_token(
        identity=str(user.id),
        expires_delta=datetime.timedelta(days=7)
    )
    
    # 修正回傳格式，確保與前端期望一致
    return jsonify({
        "status": "success",
        "message": "Login successful.",
        "data": {
            "access_token": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "role": user.role
            }
        }
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # JWT 是無狀態的，前端只需刪除 token 即可
    return jsonify({
        "status": "success",
        "message": "Successfully logged out."
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404
    return jsonify({
        "status": "success",
        "data": user.serialize()
    }), 200

@auth_bp.route('/validate', methods=['GET'])
@jwt_required()
def validate_token():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "role": user.role
    }), 200
