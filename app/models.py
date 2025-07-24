from flask_login import UserMixin
from .extensions import db
from datetime import datetime

# 2025/07/07 Neat version of the database model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    role = db.Column(db.String(32), default='user') # user, admin, umpire, judge, organizer

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role
            # 你可以根據需要加其他欄位
        }
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

class Tournament(db.Model):
    __tablename__ = 'tournaments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='Upcoming') # Upcomming, Ongoing, Completed
    events = db.relationship('Event', backref='tournament', lazy=True, cascade='all, delete-orphan')

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(10), nullable=False) # MS, WS, MD, WD, XD
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'), nullable=False)
    groups = db.relationship('Group', backref='event', lazy=True, cascade='all, delete-orphan')

class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    format_id = db.Column(db.Integer, db.ForeignKey('formats.id'), nullable=False)

class Format(db.Model):
    __tablename__ = 'formats'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False, unique=True)
    rules = db.Column(db.Text)
    group_size = db.Column(db.Integer)

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    event_type = db.Column(db.String(10), nullable=False) # MS, WS, MD, WD, XD

    # the relationship between matches (only for elimination matches)
    """
    For elimination matches, we need to have the following fields:
    - round: Round number. eg: Round 1 match 1 would be R1-M1
    - match_number: Match number. eg: Round 1 match 2 would be R1-M2
    - prev_match1_id: ID of the previous match of player 1. eg: in R2-M1, player1 is the winner of R1-M1, so prev_match1_id is match.id of R1-M1
    - prev_match2_id: ID of the previous match of player 2. eg: in R2-M1, player2 is the winner of R1-M2, so prev_match2_id is match.id of R1-M2
    - next_match_id: ID of the next match of the winner of the previous match. eg: in R2-M1, player1 is the winner of R1-M1, so next_match_id is match.id of R2-M1
    - player1_from_match: ID of the player 1 of the previous match. eg: in R2-M1, player1 is the winner of R1-M1, so player1_from_match is user.id of player1
    - player2_from_match: ID of the player 2 of the previous match. eg: in R2-M1, player2 is the winner of R1-M2, so player2_from_match is user.id of player2
    """
    batch = db.Column(db.Integer, nullable=True)
    court = db.Column(db.Integer, nullable=True)
    scheduled_time = db.Column(db.DateTime, nullable=True)
    actual_start_time = db.Column(db.DateTime, nullable=True)
    actual_end_time = db.Column(db.DateTime, nullable=True)
    
    round = db.Column(db.Integer, nullable=True)
    match_number = db.Column(db.Integer, nullable=True)
    prev_match1_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=True)
    prev_match2_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=True)
    next_match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=True)
    player1_from_match = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=True)
    player2_from_match = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=True)

    # for single matches
    player1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    player2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # names for single players
    player1_name = db.Column(db.String(100), nullable=True)
    player2_name = db.Column(db.String(100), nullable=True)

    # for doubles matches
    team1_player1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    team1_player2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    team2_player1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    team2_player2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # names for double players
    team1_player1_name = db.Column(db.String(100), nullable=True)
    team1_player2_name = db.Column(db.String(100), nullable=True)
    team2_player1_name = db.Column(db.String(100), nullable=True)
    team2_player2_name = db.Column(db.String(100), nullable=True)

    # score
    player1_score = db.Column(db.Integer, default=0)
    player2_score = db.Column(db.Integer, default=0)

    # winner
    winner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    status = db.Column(db.String(20), default='pending')
    umpire_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

class Registration(db.Model):
    __tablename__ = 'registrations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, confirmed, rejected
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)

    player_first_name = db.Column(db.String(100), nullable=False)
    player_last_name = db.Column(db.String(100), nullable=False)
    player_email = db.Column(db.String(100), nullable=False)
    
    # doubles
    partner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    partner_first_name = db.Column(db.String(100), nullable=True)  # if partner does not exist in the database, use this field to store the partner's name
    partner_last_name = db.Column(db.String(100), nullable=True)  # if partner does not exist in the database, use this field to store the partner's name
    partner_email = db.Column(db.String(100), nullable=True)

    tournament = db.relationship('Tournament', backref='registrations')
    user = db.relationship('User', foreign_keys=[user_id], backref='registrations')
    event = db.relationship('Event', backref='registrations')
    group = db.relationship('Group', backref='registrations')
    partner = db.relationship('User', foreign_keys=[partner_id], backref='partner_registrations')

    @classmethod
    def create_registration(cls, **args):
        registration = cls(**args)
        return registration

class Schedule(db.Model):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'), nullable=False)

    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    total_courts = db.Column(db.Integer, nullable=False)
    court_names = db.Column(db.JSON, nullable=True)
    match_duration = db.Column(db.Integer, nullable=False, default=30)
    
    status = db.Column(db.String(20), default='draft')

    total_matches = db.Column(db.Integer, default=0)
    total_batches = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    generated_at = db.Column(db.DateTime, nullable=True)
    
    # 明確指定外鍵
    tournament = db.relationship('Tournament', foreign_keys=[tournament_id], backref='schedules')
    schedule_items = db.relationship('ScheduleItem', backref='schedule', cascade='all, delete-orphan')

class ScheduleItem(db.Model):
    __tablename__ = 'schedule_items'
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    
    batch_number = db.Column(db.Integer, nullable=False)  
    order_in_batch = db.Column(db.Integer, nullable=False) 
    court_number = db.Column(db.Integer, nullable=False)
    
    scheduled_date = db.Column(db.Date, nullable=False)
    scheduled_start_time = db.Column(db.DateTime, nullable=False)
    scheduled_end_time = db.Column(db.DateTime, nullable=False)
    
    status = db.Column(db.String(20), default='scheduled')  # scheduled, ongoing, completed, delayed, cancelled
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    match = db.relationship('Match', backref='schedule_items')



    


