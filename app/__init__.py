from flask import Flask
from config import Config
from .extensions import db, login_manager, socketio
# from . import models  # 確保模型被載入 (前提是我把目前在db中的class User寫到models.py中)
from . import models

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 必須在 db.init_app 前設定 SQLALCHEMY_DATABASE_URI
    # 確認 config_class 有正確設定，或在此直接覆寫：
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database.db'  # 根據實際路徑調整
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev'
    # app.config.from_mapping(SECRET_KEY='dev')
    
    # 初始化擴充套件 (不要調用 models.init_app)
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app, async_mode='eventlet')
    
    # 註冊 user_loader
    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))
    
    # 建立資料庫表格（如果不存在）
    with app.app_context():
        db.create_all()
    
    # 註冊藍圖
    from .routes import (
        home_blueprint, scoreboard_blueprint, 
        umpire_blueprint, admin_blueprint, users_blueprint,
        match_blueprint, manage_match_blueprint, create_match_blueprint,
        clear_all_match_blueprint, change_match_status_blueprint,
        assign_umpire_blueprint
    )
    app.register_blueprint(home_blueprint)
    app.register_blueprint(scoreboard_blueprint)
    app.register_blueprint(umpire_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(users_blueprint)
    app.register_blueprint(match_blueprint)
    app.register_blueprint(manage_match_blueprint)
    app.register_blueprint(create_match_blueprint)
    app.register_blueprint(clear_all_match_blueprint)
    app.register_blueprint(change_match_status_blueprint)
    app.register_blueprint(assign_umpire_blueprint)
    from . import auth
    app.register_blueprint(auth.bp)

    # make sure that the admin account exist
    with app.app_context():
        db.create_all()
        from app.models import User
        from werkzeug.security import generate_password_hash
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password=generate_password_hash('admin'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()

    
    
    return app