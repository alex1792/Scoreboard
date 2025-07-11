# app/scoreboard.py
from flask import Blueprint, jsonify
from .extensions import socketio

scoreboard_bp = Blueprint('scoreboard', __name__, url_prefix='/api/scoreboard')

@scoreboard_bp.route('/')
def scoreboard_home():
    """記分板首頁"""
    return jsonify({
        "status": "success", 
        "message": "Scoreboard API is running"
    })

# WebSocket 事件處理
@socketio.on('connect', namespace='/scoreboard')
def handle_scoreboard_connect():
    print("[WebSocket] Client connected to /scoreboard namespace")

@socketio.on('disconnect', namespace='/scoreboard')
def handle_scoreboard_disconnect():
    print("[WebSocket] Client disconnected from /scoreboard namespace")
