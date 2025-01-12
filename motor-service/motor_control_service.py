import json
import requests

from PCA9685 import PCA9685

class MotorControl():
    def __init__(self, max_speed=80, min_speed=0, trim=0):
        self.PWMA = 0
        self.AIN1 = 1
        self.AIN2 = 2
        self.PWMB = 5
        self.BIN1 = 3
        self.BIN2 = 4
        self.pwm = PCA9685(0x40, debug=False)
        self.pwm.setPWMFreq(100)
        self.max_speed = max_speed
        self.min_speed = min_speed
        self.trim = 0

    def Run(self, motor, direction, speed):
        if speed > 100 or speed < 0:
            raise Exception("Speed must be between 0 and 100")
        if direction not in ['forward', 'backward']:
            raise Exception("Direction must be 'forward' or 'backward'")
        if motor not in ['left', 'right']:
            raise Exception("Motor must be 'left' or 'right'")
        # scale speed to the range between min_speed and max_speed
        speed = int(((speed / 100) * (self.max_speed - self.min_speed) + self.min_speed))
        # apply trim (positive for right engine bias)
        if motor == 'right':
            speed += int(self.trim / 2)
        elif motor == 'left':
            speed -= int(self.trim / 2)
        speed -= self.trim / 2
        print(speed)
        if motor == 'left':
            self.pwm.setDutycycle(self.PWMA, speed)
            if direction == 'forward':
                self.pwm.setLevel(self.AIN1, 0)
                self.pwm.setLevel(self.AIN2, 1)
            elif direction == 'backward':
                self.pwm.setLevel(self.AIN1, 1)
                self.pwm.setLevel(self.AIN2, 0)
        elif motor == 'right':
            self.pwm.setDutycycle(self.PWMB, speed)
            if direction == 'forward':
                self.pwm.setLevel(self.BIN1, 0)
                self.pwm.setLevel(self.BIN2, 1)
            elif direction == 'backward':
                self.pwm.setLevel(self.BIN1, 1)
                self.pwm.setLevel(self.BIN2, 0)

    def Stop(self, motor):
        if motor not in ['left', 'right']:
            raise Exception("Motor must be 'left' or 'right'")
        if motor == 'left':
            self.pwm.setDutycycle(self.PWMA, 0)
        elif motor == 'right':
            self.pwm.setDutycycle(self.PWMB, 1)

class MotorControlService:
    def __init__(self, motor_control, restApiUrl, apiToken):
        self.motor_control = motor_control
        self.restApiUrl = restApiUrl
        self.apiToken = apiToken
        self.authHeader = {'Authorization': f'{self.apiToken}'}
        try:
            settings = requests.get(f"{self.restApiUrl}/settings", headers=self.authHeader).json()
            print(settings)
            for setting in settings:
                if setting["settingName"] == "maxMotorPower":
                    self.motor_control.max_speed = int(setting["value"])
                elif setting["settingName"] == "motorTrim":
                    self.motor_control.trim = int(setting["value"])
        except Exception as e:
            print(f"Error in fetching motor control settings: {e}")

    def handle_motor_action(self, params, motor):
        match params["action"]:
            case "stop":
                self.motor_control.Stop(motor)
            case "drive":
                thrust = params["thrust"]
                direction = 'forward' if thrust >= 0 else 'backward'
                self.motor_control.Run(motor, direction, abs(thrust))

    def handle_motor_control_msg(self, params):
        left_motor = params["leftMotor"]
        right_motor = params["rightMotor"]
        self.handle_motor_action(left_motor, "left")
        self.handle_motor_action(right_motor, "right")

    def _set(self, params):
        print(self.apiToken)
        if "maxPower" in params:
            if params["maxPower"] < 0 or params["maxPower"] > 100:
                raise Exception("Max speed must be between 0 and 100")
            self.motor_control.max_speed = params["maxPower"]
            try:
                requests.post(f"{self.restApiUrl}/settings", json={"name": "maxMotorPower", "value": str(params["maxPower"])}, headers=self.authHeader)
            except Exception as e:
                print(f"Error in updating setting: {e}")
        if "motorTrim" in params:
            if params["motorTrim"] < -50 or params["motorTrim"] > 50:
                raise Exception("Trim must be between -100 and 100")
            self.motor_control.trim = params["motorTrim"]
            try:
                requests.post(f"{self.restApiUrl}/settings", json={"name": "motorTrim", "value": str(params["motorTrim"])}, headers=self.authHeader)
            except Exception as e:
                print(f"Error in updating setting: {e}")

    def handle_message(self, msg):
        try:
            event = json.loads(msg)
            match event["type"]:
                case "motorControl":
                    self.handle_motor_control_msg(event["params"])
                    return "ack"
                case "settings":
                    print('settings')
                    self._set(event["params"])
                    return "ack"
        except Exception as e:
            print(f"Error in processing control message: {msg}, {e}")
            return "error"

    def stopMotors(self):
        self.motor_control.Stop("left")
        self.motor_control.Stop("right")
