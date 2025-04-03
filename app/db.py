import sqlite3
from flask import current_app, g

class User:
    def __init__(self, id, username, password, is_judge):
        self.id = id
        self.username = username
        self.password = password
        self.is_judge = is_judge

class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.init_users()
        self.init_db()
    
    @staticmethod
    def get_db():
        if 'db' not in g:
            g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row

        return g.db


    def init_users(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users
            (id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, is_judge BOOL)
        ''')
        self.conn.commit()

    
    def init_db(self):
        # self.cursor.execute()
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
                    FOREIGN KEY (player1_id) REFERENCES players (id),
                    FOREIGN KEY (player2_id) REFERENCES players (id)
                )
            ''')
        
        # add two players
        self.add_player('Player1')
        self.add_player('Player2')

        self.cursor.execute('SELECT id FROM players WHERE name = ?', ('Player1',))
        p1_id = self.cursor.fetchone()[0]

        self.cursor.execute('SELECT id FROM players WHERE name = ?', ('Player2',))
        p2_id = self.cursor.fetchone()[0]

        # create a new game
        self.add_match(p1_id, p2_id)
        self.conn.commit()

    def add_player(self, name):
        self.cursor.execute('INSERT INTO players (name) VALUES (?)', (name,))
        self.conn.commit()
        # self.conn.close()

    def add_match(self, player1_id, player2_id):
        self.cursor.execute('INSERT INTO matches (player1_id, player2_id) VALUES (?, ?)', (player1_id, player2_id))
        self.conn.commit()
        # self.conn.close()

    def update_score(self, match_id, score1, score2):
        self.cursor.execute('UPDATE matches SET score1 = ?, score2 = ?, WHERE id = ?', (score1, score2, match_id))
        self.conn.commit()
        # self.conn.close()

    def get_match_info(self):
        self.cursor.execute('''
            SELECT p1.name AS player1_name, p2.name AS player2_name, m.score1, m.score2
            FROM matches m
            JOIN players p1 ON m.player1_id = p1.id
            JOIN players p2 ON m.player2_id = p2.id
            ORDER BY m.id DESC LIMIT 1
        ''')
        row = self.cursor.fetchone()
        self.conn.close()
        
        if row:
            return {
                'player1_name': row[0],
                'player2_name': row[1],
                'score1': row[2],
                'score2': row[3]
            }
        else:
            return None
        
    def get_user(self, user_id):
        self.cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user_info = self.cursor.fetchone()
        if user_info:
            return User(*user_info)
        else:
            return None

    
    def close(self):
        self.conn.close()

def load_user(user_id):
    return Database.get_user(user_id)
