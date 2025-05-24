import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from .extensions import db  # 從 extensions.py 導入 SQLAlchemy 實例
from .models import User, Player  # 導入 ORM 模型

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                # 使用 ORM 建立 User 和 Player
                new_user = User(
                    username=username,
                    password=generate_password_hash(password),
                    role='user'  # 新增角色欄位
                )
                db.session.add(new_user)
                db.session.flush()  # 獲取自動生成的 user.id

                new_player = Player(id=new_user.id, name=username)
                db.session.add(new_player)
                
                db.session.commit()
                return redirect(url_for("auth.login"))

            except Exception as e:
                db.session.rollback()
                if 'UNIQUE constraint failed: users.username' in str(e):
                    error = f"User {username} is already registered."
                else:
                    error = "Registration failed. Please try again."

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        
        # 使用 ORM 查詢
        user = User.query.filter_by(username=username).first()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'

        if error is None:
            login_user(user)  # 直接傳入 ORM 物件
            return redirect(url_for('home_blueprint.home'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    # Flask-Login 已自動處理 current_user
    # 此函式可移除或用於其他用途
    pass

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home_blueprint.home'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view



# import functools

# from flask import (
#     Blueprint, flash, g, redirect, render_template, request, session, url_for
# )
# from flask_login import login_user, logout_user
# from werkzeug.security import check_password_hash, generate_password_hash
# from .models import Database, User

# bp = Blueprint('auth', __name__, url_prefix='/auth')

# @bp.route('/register', methods=('GET', 'POST'))
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         db = Database.get_db()
#         error = None

#         if not username:
#             error = 'Username is required.'
#         elif not password:
#             error = 'Password is required.'

#         if error is None:
#             try:
#                 cursor = db.cursor()
#                 cursor.execute(
#                     "INSERT INTO users (username, password) VALUES (?, ?)",
#                     (username, generate_password_hash(password)),
#                 )                
#                 user_id = cursor.lastrowid
#                 cursor.execute('INSERT INTO players (id, name) VALUES (?, ?)', (user_id, username))
#                 db.commit()
#             except db.IntegrityError:
#                 error = f"User {username} is already registered."
#             else:
#                 return redirect(url_for("auth.login"))

#         flash(error)

#     return render_template('auth/register.html')

# @bp.route('/login', methods=('GET', 'POST'))
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         db = Database.get_db()
#         error = None
#         user = db.execute(
#             'SELECT * FROM users WHERE username = ?', (username,)
#         ).fetchone()

#         if user is None:
#             error = 'Incorrect username.'
#         elif not check_password_hash(user['password'], password):
#             error = 'Incorrect password.'

#         if error is None:
#             user_info = User(user['id'], user['username'], user['password'])
#             login_user(user_info)  # 使用 login_user
#             return redirect(url_for('home_blueprint.home'))

#         flash(error)

#     return render_template('auth/login.html')

# @bp.before_app_request
# def load_logged_in_user():
#     user_id = session.get('user_id')

#     if user_id is None:
#         g.user = None
#     else:
#         g.user = Database.get_db().execute(
#             'SELECT * FROM users WHERE id = ?', (user_id,)
#         ).fetchone()

# @bp.route('/logout')
# def logout():
#     logout_user()
#     session.clear()
#     # redirect to the new url. If we use render_template(), we will not redirect to the page we want!
#     # when we want to use the function 'url_for()', the parameter should be blueprint we registered at blueprints.py
#     return redirect(url_for('home_blueprint.home'))

# def login_required(view):
#     @functools.wraps(view)
#     def wrapped_view(**kwargs):
#         if g.user is None:
#             return redirect(url_for('auth.login'))

#         return view(**kwargs)

#     return wrapped_view