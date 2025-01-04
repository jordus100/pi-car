import sys
from functools import wraps

from flask import Blueprint, request, jsonify, session

from services.AuthService import AuthService
from services.UserService import UserService

UserBp = Blueprint('User', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not (session.get('user_id') and session.get('is_admin')):
            return jsonify({'message': 'Unauthorized'}), 401
        return(f(*args, **kwargs))
    return decorated_function

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        userId = session.get('user_id')
        if not userId:
            return jsonify({'message': 'Unauthorized'}), 401
        return (f(*args, **kwargs))
    return decorated_function

@UserBp.route('/add_user', methods=['POST'])
@admin_required
def add_user():
    data = request.get_json()
    if not all(key in data for key in ('username', 'password')):
        return jsonify({'message': 'Username and password are required'}), 400

    if UserService.user_exists(data['username']):
        return jsonify({'message': 'Username already exists'}), 400

    UserService.add_user(data['username'], data['password'])
    return jsonify({'message': 'User added successfully'}), 201


@UserBp.route('/users', methods=['GET'])
@admin_required
def list_users():
    users = UserService.get_all_users()
    return jsonify(users)


@UserBp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
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
    print(data, file=sys.stderr)
    if not all(key in data for key in ('username', 'password')):
        return jsonify({'message': 'Username and password are required'}), 400

    if not AuthService.authenticate_user(data['username'], data['password']):
        return jsonify({'message': 'Invalid username or password'}), 401

    is_admin = False
    if UserService.is_admin(UserService.get_user_by_username(data['username'])):
        session['is_admin'] = True
        is_admin = True
    else:
        session['is_admin'] = False

    session['user_id'] = UserService.get_user_by_username(data['username']).id
    return jsonify({'message': 'Login successful', 'isAdmin': is_admin}), 200


@UserBp.route('/logout', methods=['POST'])
@login_required
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logout successful'}), 200


@UserBp.route('/check_session', methods=['GET'])
@login_required
def check_session():
    user = UserService.get_user_by_id(session.get('user_id'))
    if user is None:
        return jsonify({'message': 'User not found'}), 404
    return jsonify({'message': 'User is logged in', 'username': user.username, 'isAdmin': user.is_admin}), 200


@UserBp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    data = request.get_json()
    if not all(key in data for key in ('old_password', 'new_password')):
        return jsonify({'message': 'Old password and new password are required'}), 400

    if not AuthService.change_password(session['user_id'], data['old_password'], data['new_password']):
        return jsonify({'message': 'Old password is incorrect or update failed'}), 401

    return jsonify({'message': 'Password changed successfully'}), 200
