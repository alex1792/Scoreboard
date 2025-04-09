import sqlite3
from flask import current_app, g
from flask_login import UserMixin, login_manager

class User(UserMixin):
    def __init__(self, id, username, password, is_judge=False):
        self.id = id
        self.username = username
        self.password = password
        self.is_judge = is_judge

    def __repr__(self):
        return f"User('{self.username}')"

class Database:
    # constructor
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row # 這行可以解決我把一些query function封裝在Database class中後 在routes.py中沒辦法顯示的問題
        self.cursor = self.conn.cursor()
        self.init_users()
        self.init_db()
    
    # a function that allows other code to access the Database.db
    @staticmethod
    def get_db():
        if 'db' not in g:
            g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row

        return g.db

    # initialize users table in database
    # for login use
    def init_users(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users
            (id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, is_judge BOOL)
        ''')
        self.conn.commit()

    # initialize database table
    # table 'players' is used for players info
    # table 'matches' is used to preserve matche scores
    def init_db(self):
        self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                )
            ''')
        self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player1_id INTEGER,
                    player2_id INTEGER,
                    score1 INTEGER NOT NULL DEFAULT 0,
                    score2 INTEGER NOT NULL DEFAULT 0,
                    status TEXT,
                    FOREIGN KEY (player1_id) REFERENCES players (id),
                    FOREIGN KEY (player2_id) REFERENCES players (id)
                )
            ''')
        
        # add two players
        self.add_player('Player1')
        self.add_player('Player2')

        self.conn.commit()

    # add player into table players
    def add_player(self, name):
        self.cursor.execute('INSERT INTO players (name) VALUES (?)', (name,))
        self.conn.commit()
    
    # add match into table matches
    def add_match(self, player1_id, player2_id):
        self.cursor.execute('INSERT INTO matches (player1_id, player2_id, status) VALUES (?, ?, ?)', (player1_id, player2_id, 'scheduled'))
        self.conn.commit()

    # update scores
    def update_score(self, player_id, match_info, score):
        # update player1 score
        if player_id == match_info['player1_id']:
            if score == 1:
                self.cursor.execute('''
                                    UPDATE matches 
                                    SET score1 = score1 + 1 
                                    WHERE player1_id = ?''', (player_id,))
            elif score == -1:
                self.cursor.execute('''
                                    UPDATE matches 
                                    SET score1 = score1 - 1 
                                    WHERE player1_id = ? AND score1 > 0''', (player_id,))
        
        # update player2 score
        elif player_id == match_info['player2_id']:
            if score == 1:
                self.cursor.execute('''
                                    UPDATE matches 
                                    SET score2 = score2 + 1 
                                    WHERE player2_id = ?''', (player_id,))
            elif score == -1:
                self.cursor.execute('''
                                    UPDATE matches 
                                    SET score2 = score2 - 1 
                                    WHERE player2_id = ? AND score2 > 0''', (player_id,))
        
        self.conn.commit()

    # get match information, can be used for search match
    def get_match_info(self):
        self.cursor.execute('''
            SELECT 
                m.id AS match_id,
                m.player1_id,
                p1.name AS player1_name,
                m.player2_id,
                p2.name AS player2_name,
                m.score1,
                m.score2,
                m.status
            FROM matches m
            JOIN players p1 ON m.player1_id = p1.id
            JOIN players p2 ON m.player2_id = p2.id;
        ''')
        row = self.cursor.fetchone()
        
        if row:
            return {
                'match_id': row[0],
                'player1_id': row[1],
                'player1_name': row[2],
                'player2_id': row[3],
                'player2_name': row[4],
                'score1': row[5],
                'score2': row[6],
                'status': row[7]
            }
        else:
            return None

    # get user info
    def get_user(self, user_id):
        self.cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user_info = self.cursor.fetchone()
        if user_info:
            return User(*user_info)
        else:
            return None

    # get user id by username
    def get_user_id_by_username(self, username):
        query = 'SELECT id FROM users WHERE username=?'
        self.cursor.execute(query, (username,))
        row = self.cursor.fetchone()
        print(row)
        if row:
            return row['id']
        else:
            return None

    # set user as umpire or not
    def set_umpire(self, username, is_umpire):
        self.cursor.execute('UPDATE users SET is_judge = ? WHERE username = ?', (is_umpire, username,))
        self.conn.commit()

    # close database when terminate
    def close(self):
        self.conn.close()

    # delete match by match_id
    def clear_match_by_id(self, match_id):
        query = 'DELETE FROM matches WHERE id=' + str(match_id)
        self.cursor.execute(query)
        self.conn.commit()

    # delete all match
    def clear_all_match(self):
        query = 'DELETE FROM matches'
        self.cursor.execute(query)
        self.conn.commit()

    # get all match
    def get_all_match(self):
        query = 'SELECT * FROM matches'
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    # get all users
    def get_all_users(self):
        query = 'SELECT * FROM users'
        self.cursor.execute(query)
        return self.cursor.fetchall()

    # change match status
    def change_match_status(self, new_status, match_id):
        query = 'UPDATE matches SET status = ? WHERE id = ?'
        self.cursor.execute(query, (new_status, match_id,))
        self.conn.commit()

def load_user(user_id):
    return Database.get_user(user_id)
