from werkzeug.security import generate_password_hash

from db import User
from repositories.UserRepository import UserRepository

class UserService:

    @staticmethod
    def add_user(username, password):
        if UserRepository.get_by_username(username):
            raise ValueError("Username already exists")
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        UserRepository.save(new_user)
        return new_user

    @staticmethod
    def get_all_users():
        users = UserRepository.get_all()
        return [{"id": user.id, "username": user.username, "is_admin": user.is_admin} for user in users]

    @staticmethod
    def get_user_by_id(user_id):
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        return user

    @staticmethod
    def get_user_by_username(username):
        user = UserRepository.get_by_username(username)
        if not user:
            raise ValueError(f"User with username {username} not found")
        return user

    @staticmethod
    def user_exists(username):
        return UserRepository.get_by_username(username) is not None

    @staticmethod
    def delete_user(user_id):
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        if user.is_admin:
            raise ValueError("Cannot delete admin user")
        UserRepository.delete(user)
        return user

    @staticmethod
    def is_admin(user):
        """Check if the user has admin privileges."""
        return user.is_admin
