import eventlet
eventlet.monkey_patch()

from app import create_app
from app.extensions import db, socketio  # db, socketio 都是 extensions.py 中的全域實例

app = create_app()

if __name__ == '__main__':
    # 用 app context 初始化資料表（只需做一次）
    with app.app_context():
        db.create_all()  # 自動建立所有 ORM 定義的資料表

    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
