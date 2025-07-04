import eventlet
eventlet.monkey_patch()

from app import create_app
from app.extensions import db, socketio  # db, socketio 都是 extensions.py 中的全域實例

app = create_app()

# if __name__ == '__main__':
#     # 用 app context 初始化資料表（只需做一次）
#     with app.app_context():
#         db.create_all()  # 自動建立所有 ORM 定義的資料表

#     socketio.run(app, host='0.0.0.0', port=5001, debug=True)



if __name__ == '__main__':
    # 用 app context 初始化資料表
    with app.app_context():
        # 刪除所有表格並重新建立（注意：這會刪除所有資料）
        # db.drop_all()
        db.create_all()
        
        # 初始化基本 Format
        # from app.models import Format
        # formats = [
        #     Format(type='round_robin', rules='Round Robin format'),
        #     Format(type='elimination', rules='Elimination format')
        # ]
        # for fmt in formats:
        #     db.session.add(fmt)
        # db.session.commit()
        
        # print("Database tables recreated and formats initialized successfully!")

    socketio.run(app, host='0.0.0.0', port=5001, debug=True)