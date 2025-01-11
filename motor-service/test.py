import os
from dotenv import load_dotenv

from main import startApp
from motor_control_service import MotorControlService


class MockMotorControlService:
    def __init__(self, min_speed=0, max_speed=100):
        self.min_speed = min_speed
        self.max_speed = max_speed

    def handle_message(self, msg):
        pass

    def handle_motor_control_msg(self, params):
        pass

    def stopMotors(self):
        pass

class MockMotorControl:
    def __init__(self, min_speed, max_speed, trim=0):
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.trim = trim

    def Run(self, motor, direction, speed):
        pass

    def Stop(self, motor):
        pass

if __name__ == "__main__":
    load_dotenv()
    apiToken = os.getenv('API_TOKEN')
    motorService = MotorControlService(MockMotorControl(0, 100), "http://localhost:5000/api", apiToken)

    print("Starting test")
    startApp(motorService)
