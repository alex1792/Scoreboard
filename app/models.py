from flask_login import UserMixin
from .extensions import db
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_judge = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(32), default='user')  # create role attribute, different role can access different services on the system

    def has_role(self, role_name):
        return self.role == role_name
    
    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role
            # 你可以根據需要加其他欄位
        }

class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(32), nullable=False)
    player1_name = db.Column(db.String(64), nullable=False)
    player2_name = db.Column(db.String(64), nullable=False)
    score1 = db.Column(db.Integer, default=0)
    score2 = db.Column(db.Integer, default=0)
    status = db.Column(db.String(32))
    umpire_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    umpire = db.relationship('User', foreign_keys=[umpire_id])
    # player1_id = db.Column(db.Integer, db.ForeignKey('players.id'))
    # player2_id = db.Column(db.Integer, db.ForeignKey('players.id'))
    # player1 = db.relationship('Player', foreign_keys=[player1_id])
    # player2 = db.relationship('Player', foreign_keys=[player2_id])

# class Match(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
#     event_type = db.Column(db.String(50), nullable=False)  # 'singles', 'doubles'
#     group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    
#     # 統一使用 ID，根據 event_type 判斷是 player_id 還是 doubles_team_id
#     participant1_id = db.Column(db.Integer, nullable=False)
#     participant2_id = db.Column(db.Integer, nullable=False)
    
#     participant1_score = db.Column(db.Integer, default=0)
#     participant2_score = db.Column(db.Integer, default=0)
#     status = db.Column(db.String(20), default='pending')
#     umpire_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    

class Tournament(db.Model):
    __tablename__ = 'tournaments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    # max_participants = db.Column(db.Integer)
    registration_deadline = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關係定義
    events = db.relationship('Event', backref='tournament', lazy=True, cascade='all, delete-orphan')

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    category = db.Column(db.String(10), nullable=False)  # MS, WS, MD, WD, XD
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'), nullable=False)
    max_participants = db.Column(db.Integer)
    status = db.Column(db.String(20), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 關係定義
    groups = db.relationship('Group', backref='event', lazy=True, cascade='all, delete-orphan')

class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    format_id = db.Column(db.Integer, db.ForeignKey('formats.id'), nullable=False)
    max_participants = db.Column(db.Integer)
    status = db.Column(db.String(20), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Format(db.Model):
    __tablename__ = 'formats'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False, unique=True)
    rules = db.Column(db.Text)
    group_size = db.Column(db.Integer)  # 用於 round robin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 關係定義 - 一對多關係
    groups = db.relationship('Group', backref='format', lazy=True)


# 2025/07/07 新增版本
