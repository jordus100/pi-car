import os

from flask import Blueprint, request, jsonify
import requests

from controllers.UserController import admin_required, login_required

RobotBp = Blueprint('Robot', __name__)

controlServicePort = os.getenv("MOTOR_SERVICE_INT_REST_PORT", 8081)

@RobotBp.route('/control/startSession', methods=['POST'])
@admin_required
def add_user():
    response = requests.post(f"http://localhost:{controlServicePort}/startControlSession")
    return jsonify(response.json()), response.status_code

