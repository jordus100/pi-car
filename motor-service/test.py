from main import startApp


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

if __name__ == "__main__":
    motorService = MockMotorControlService()
    startApp(motorService)
