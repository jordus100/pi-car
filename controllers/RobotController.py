import os
import subprocess

from flask import Blueprint, request, jsonify
import requests

from controllers.UserController import admin_required, login_required
from db import Settings
from repositories.SettingsRepository import SettingsRepository
from services import SettingService

RobotBp = Blueprint('Robot', __name__)

controlServicePort = os.getenv("MOTOR_SERVICE_INT_REST_PORT", 8081)

@RobotBp.route('/control/startSession', methods=['POST'])
@login_required
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

@RobotBp.route('/zerotier', methods=['POST'])
@admin_required
def join_zerotier():
    data = request.get_json()
    if not data['networkId']:
        return jsonify({'message': 'Network ID is required'}), 400
    ret = subprocess.call(f"zerotier-cli join {data['networkId']}", shell=True)
    if ret != 0:
        return jsonify({'message': 'Failed to join network'}), 501
    return jsonify(f"Robot joined ZeroTier network {data['networkId']}", 201)

@RobotBp.route('/shutdown', methods=['POST'])
@login_required
def shutdown():
    os.system('sudo poweroff &')
    return jsonify(f"Robot shutting down", 201)

@RobotBp.route('/sftp', methods=['POST'])
@admin_required
def set_sftp():
    data = request.get_json()
    SettingService.save_sftp_settings(data)
    return jsonify(), 201

@RobotBp.route('/sftp', methods=['GET'])
@admin_required
def get_sftp():
    sftp = SettingService.get_sftp_settings()
    return jsonify({'host': sftp['sftp_host'], 'port': sftp['sftp_port'], 'username': sftp['sftp_username'], 'password': sftp['sftp_password']}), 200

@RobotBp.route('/ip', methods=['GET'])
@admin_required
def get_ip():
    ip = subprocess.check_output("ip -br a", shell=True).decode().strip()
    ipData = []
    for line in ip.split('\n'):
        ipData.append(' '.join(line.split()))
    return jsonify(ipData), 200
