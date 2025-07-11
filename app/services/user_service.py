# app/services/user_service.py
from ..models import User, db

class UserService:
    """用戶相關的業務邏輯服務"""
    
    @staticmethod
    def get_all_users():
        """獲取所有用戶"""
        users = User.query.all()
        users_data = []
        for user in users:
            user_data = {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role
            }
            users_data.append(user_data)
        return users_data

    @staticmethod
    def get_user_by_id(user_id):
        """根據ID獲取用戶"""
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_name(first_name, last_name):
        """根據姓名獲取用戶"""
        return User.query.filter_by(first_name=first_name, last_name=last_name).first()

    @staticmethod
    def update_user_role(user_id, new_role):
        """更新用戶角色"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        user.role = new_role
        db.session.commit()
        return user

    @staticmethod
    def update_user_role_by_username(username, new_role):
        """根據用戶名更新用戶角色"""
        user = User.query.filter_by(username=username).first()
        if not user:
            raise ValueError("User not found")
        
        user.role = new_role
        db.session.commit()
        return user