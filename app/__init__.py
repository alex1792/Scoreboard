from flask import Flask
from flask_cors import CORS
from datetime import timedelta
from .extensions import db, socketio, jwt  # 移除 login_manager
from . import models
import os
import secrets

def create_app():
    # app = Flask(__name__)
    app = Flask(__name__, 
                static_folder='../frontend/build/static',  # 指向 build 的 static 資料夾
                template_folder='../frontend/build')       # 指向 build 資料夾
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
            user_data = {
                'username': 'admin',
                'password': generate_password_hash('admin'),
                'role': 'admin',
                'first_name': 'Admin',
                'last_name': 'Admin'
            }
            
            admin = User(**user_data)
            db.session.add(admin)
            db.session.commit()

        # 確保基本 Format 存在
        from .models import Format
        if not Format.query.filter_by(type='round_robin').first():
            format_data = {
                'type': 'round_robin',
                'rules': 'Round Robin format',
                'group_size': 4
            }
            
            round_robin_format = Format(**format_data)
            db.session.add(round_robin_format)
        
        if not Format.query.filter_by(type='elimination').first():
            elimination_format_data = {
                'type': 'elimination',
                'rules': 'Elimination format',
                'group_size': None  # 淘汰賽不需要分組大小
            }
            
            elimination_format = Format(**elimination_format_data)
            db.session.add(elimination_format)
        
        db.session.commit()
    
    from .blueprints import register_blueprints
    register_blueprints(app)

    return app
