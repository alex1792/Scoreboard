from flask import Flask
from flask_cors import CORS
from datetime import timedelta
from .extensions import db, socketio, jwt  # 移除 login_manager
from . import models

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}) # 因為前端運行在localhost:3000, 後端運行在localhost:5001, 屬於跨域請求, 必須使用CORS
    
    # 手動設定所有必要參數
    app.config.update(
        SQLALCHEMY_DATABASE_URI='sqlite:///../database.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY='your-secret-key-here',  # 生產環境請用環境變數
        JWT_SECRET_KEY='your-jwt-secret-key',
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
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
    
    # 註冊藍圖（確保藍圖已改為 API 路由）
    from .auth import bp as auth_bp  # 從 auth.py 導入藍圖
    from .routes import home_blueprint  # 只導入 routes 中的藍圖
    app.register_blueprint(home_blueprint)
    app.register_blueprint(auth.bp)
    
    return app
