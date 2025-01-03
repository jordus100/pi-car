from flask import Blueprint, request, jsonify, session

from services.AuthService import AuthService
from services.UserService import UserService
import jwt

UserBp = Blueprint('User', __name__)

@UserBp.route('/add_user', methods=['POST'])
def add_user():
    admin_token = request.headers.get('Authorization')
    if not admin_token:
        return jsonify({'message': 'Token is missing'}), 401

    try:
        decoded = AuthService.decode_token(admin_token)
        if not UserService.is_admin(decoded['user_id']):
            raise jwt.InvalidTokenError
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401

    data = request.get_json()
    if not all(key in data for key in ('username', 'password')):
        return jsonify({'message': 'Username and password are required'}), 400

    if UserService.user_exists(data['username']):
        return jsonify({'message': 'Username already exists'}), 400

    UserService.add_user(data['username'], data['password'])
    return jsonify({'message': 'User added successfully'}), 201


@UserBp.route('/users', methods=['GET'])
def list_users():
    users = UserService.get_all_users()
    return jsonify(users)


@UserBp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    # check if admin's session
    userId =
    if not UserService.delete_user(user_id):
        return jsonify({"message": f"User with ID {user_id} not found or cannot be deleted."}), 404
    return jsonify({"message": f"User with ID {user_id} has been deleted."})


@UserBp.route('/generate_token', methods=['POST'])
def generate_auth_token():
    data = request.get_json()
    if not all(key in data for key in ('username', 'password')):
        return jsonify({'message': 'Username and password are required'}), 400

    token = AuthService.authenticate_user(data['username'], data['password'])
    if not token:
        return jsonify({'message': 'Invalid username or password'}), 401

    return jsonify({'token': token}), 200


@UserBp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not all(key in data for key in ('username', 'password')):
        return jsonify({'message': 'Username and password are required'}), 400

    if not AuthService.authenticate_user(data['username'], data['password']):
        return jsonify({'message': 'Invalid username or password'}), 401

    session['user_id'] = UserService.get_user_by_username(data['username'])
    return jsonify({'message': 'Login successful'}), 200


@UserBp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logout successful'}), 200


@UserBp.route('/check_session', methods=['GET'])
def check_session():
    if 'user_id' in session:
        user = UserService.get_user_by_id(session['user_id'])
        return jsonify({'message': 'User is logged in', 'username': user.username}), 200
    return jsonify({'message': 'No active session'}), 401


@UserBp.route('/change_password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    data = request.get_json()
    if not all(key in data for key in ('old_password', 'new_password')):
        return jsonify({'message': 'Old password and new password are required'}), 400

    if not AuthService.change_password(session['user_id'], data['old_password'], data['new_password']):
        return jsonify({'message': 'Old password is incorrect or update failed'}), 401

    return jsonify({'message': 'Password changed successfully'}), 200
