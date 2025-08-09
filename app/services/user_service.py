# app/services/user_service.py
from ..models import User, db

class UserService:
    """user related services(query all users, update user's role)"""
    
    @staticmethod
    def get_all_users():
        """query all users's info"""
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
        """get particular user by user_id"""
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_name(first_name, last_name):
        """serch user by first_name and last_name"""
        return User.query.filter_by(first_name=first_name, last_name=last_name).first()

    @staticmethod
    def update_user_role(user_id, new_role):
        """update user's role (admin, host, umpire, user)"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        user.role = new_role
        db.session.commit()
        return user

    @staticmethod
    def update_user_role_by_username(username, new_role):
        """update particular user's role
        
        given a username and a new_role, set that user.role to new_role
        """
        user = User.query.filter_by(username=username).first()
        if not user:
            raise ValueError("User not found")
        
        user.role = new_role
        db.session.commit()
        return user