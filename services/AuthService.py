from werkzeug.security import check_password_hash, generate_password_hash
import jwt
import datetime
from flask import current_app
from repositories.UserRepository import UserRepository

class AuthService:
    @staticmethod
    def authenticate_user(username, password):
        """Authenticate a user with their username and password."""
        user = UserRepository.get_by_username(username)
        if user and check_password_hash(user.password, password):
            return user
        return None

    @staticmethod
    def generate_token(user_id):
        """Generate a JWT token for a user."""
        payload = {
            'user_id': user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            'iat': datetime.datetime.utcnow()
        }
        return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def decode_token(token):
        """Decode a JWT token to retrieve user information."""
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

    @staticmethod
    def change_password(user, old_password, new_password):
        """Change the password for a user."""
        if not check_password_hash(user.password, old_password):
            raise ValueError("Old password is incorrect")

        user.password = generate_password_hash(new_password)
        user.save()