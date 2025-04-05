# from app import create_app
# from app.db import Database

# app = create_app()

# if __name__ == '__main__':
#     with app.app_context():
#         db_name = 'database.db'
#         db = Database(db_name)
#         db.init_db()
#         # Database.init_db()  # 初始化資料庫
#     app.run(debug=True)

import eventlet
eventlet.monkey_patch() 

from app import create_app, socketio  
from app.db import Database

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db_name = 'database.db'
        db = Database(db_name)
        db.init_db()  # initialize database
    
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)

