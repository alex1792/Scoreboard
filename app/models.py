from flask_login import UserMixin
from .extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_judge = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(32), default='user')  # create role attribute, different role can access different services on the system

    def has_role(self, role_name):
        return self.role == role_name

class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    player1_id = db.Column(db.Integer, db.ForeignKey('players.id'))
    player2_id = db.Column(db.Integer, db.ForeignKey('players.id'))
    score1 = db.Column(db.Integer, default=0)
    score2 = db.Column(db.Integer, default=0)
    status = db.Column(db.String(32))
    umpire_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    player1 = db.relationship('Player', foreign_keys=[player1_id])
    player2 = db.relationship('Player', foreign_keys=[player2_id])
    umpire = db.relationship('User', foreign_keys=[umpire_id])