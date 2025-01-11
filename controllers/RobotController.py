import os

from flask import Blueprint, request, jsonify
import requests

from controllers.UserController import admin_required, login_required
from db import Settings
from repositories.SettingsRepository import SettingsRepository

RobotBp = Blueprint('Robot', __name__)

controlServicePort = os.getenv("MOTOR_SERVICE_INT_REST_PORT", 8081)

@RobotBp.route('/control/startSession', methods=['POST'])
@admin_required
def add_user():
    response = requests.post(f"http://localhost:{controlServicePort}/startControlSession")
    return jsonify(response.json()), response.status_code

@RobotBp.route('/auth', methods=['GET'])
@login_required
def auth():
    return jsonify({"message": "Authorized"}), 200

@RobotBp.route('/settings', methods=['GET'])
@login_required
def get_settings():
    settings = SettingsRepository.get_all()
    return jsonify([{'settingName': setting.name, 'value': setting.value} for setting in settings]), 200

@RobotBp.route('/settings', methods=['POST'])
@login_required
def change_setting():
    data = request.get_json()
    if not all(key in data for key in ('name', 'value')):
        return jsonify({'message': 'Name and value are required'}), 400
    SettingsRepository.update(Settings(name = data['name'], value= data['value']))
    return jsonify(), 201

