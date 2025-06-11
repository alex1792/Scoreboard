from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from .extensions import db
from .models import User, Player
import datetime  # 用於設定 JWT 過期時間

bp = Blueprint('auth', __name__, url_prefix='/api/auth')  # 加上 /api 前綴

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({
            "status": "error",
            "message": "Username and password are required."
        }), 400

    # 檢查用戶名是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({
            "status": "error",
            "message": "Username already exists."
        }), 409

    try:
        new_user = User(
            username=username,
            password=generate_password_hash(password),
            role='user'
        )
        db.session.add(new_user)
        db.session.flush()

        new_player = Player(id=new_user.id, name=username)
        db.session.add(new_player)
        db.session.commit()

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
                    "role": new_user.role
                },
                "access_token": access_token
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": "Registration failed."
        }), 500

@bp.route('/login', methods=['POST'])
def login():
    # get username and password from frontend
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # serch user in database by username
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
    

    return jsonify({
        "status": "success",
        "message": "Login successful.",
        "data": {
            "access_token": access_token,
            "user": user.serialize()
        }
    }), 200

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # JWT 是無狀態的，前端只需刪除 token 即可
    return jsonify({
        "status": "success",
        "message": "Successfully logged out."
    }), 200

@bp.route('/me', methods=['GET'])
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
