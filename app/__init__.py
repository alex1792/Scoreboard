from flask import Flask
from flask_cors import CORS
from datetime import timedelta
from .extensions import db, socketio, jwt  # 移除 login_manager
from . import models
import os
import secrets

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}) # 因為前端運行在localhost:3000, 後端運行在localhost:5001, 屬於跨域請求, 必須使用CORS
    
    # socketio.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    
    # 自動產生 secret key（如果沒設定環境變數）
    secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    jwt_secret_key = os.environ.get('JWT_SECRET_KEY') or secrets.token_hex(32)

    # 手動設定所有必要參數
    app.config.update(
        SQLALCHEMY_DATABASE_URI='sqlite:///../database.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY=secret_key,  # 生產環境請用環境變數
        JWT_SECRET_KEY=jwt_secret_key,
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(days=7)
    )

    # 初始化擴充套件
    db.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app, async_mode='eventlet', cors_allowed_origins="*")
    
    # 建立資料庫表格
    with app.app_context():
        db.create_all()
        # 確保 admin 帳號存在
        from .models import User
        from werkzeug.security import generate_password_hash
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password=generate_password_hash('admin'),
                role='admin',
                first_name='Admin',
                last_name='Admin'
            )
            db.session.add(admin)
            db.session.commit()

        # 確保基本 Format 存在
        from .models import Format
        if not Format.query.filter_by(type='round_robin').first():
            round_robin_format = Format(
                type='round_robin',
                rules='Round Robin format',
            )
            db.session.add(round_robin_format)
        
        if not Format.query.filter_by(type='elimination').first():
            elimination_format = Format(
                type='elimination',
                rules='Elimination format',
            )
            db.session.add(elimination_format)
        
        db.session.commit()
    
    # 註冊所有 Blueprints
    # from .routes import (
    #     home_blueprint,
    #     scoreboard_blueprint,
    #     admin_blueprint,
    #     users_blueprint,
    #     match_blueprint         
    #     # manage_match_blueprint,
    #     # create_match_blueprint,
    #     # assign_umpire_blueprint  
    # )
    # from .auth import bp as auth_bp
    from .blueprints import register_blueprints
    register_blueprints(app)

    # 註冊 Blueprints 並指定 url_prefix
    # app.register_blueprint(home_blueprint, url_prefix='/api/home')
    # app.register_blueprint(admin_blueprint, url_prefix='/api/admin')
    # app.register_blueprint(users_blueprint, url_prefix='/api/users')
    # app.register_blueprint(match_blueprint, url_prefix='/api/matches')
    # # app.register_blueprint(manage_match_blueprint, url_prefix='/api/manage-matches')
    # # app.register_blueprint(create_match_blueprint, url_prefix='/api/create-match')
    # # app.register_blueprint(assign_umpire_blueprint, url_prefix='/api/assign-umpire')
    # app.register_blueprint(auth_bp, url_prefix='/api/auth')  # 假設 auth_bp 的路由前綴是 /auth

    return app
