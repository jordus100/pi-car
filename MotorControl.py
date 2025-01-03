#!/home/pi/dyplom/venv2/bin/python
import time
import os

from PCA9685 import PCA9685

class MotorControl():
    def __init__(self, max_speed=80, min_speed=0):
        self.PWMA = 0
        self.AIN1 = 1
        self.AIN2 = 2
        self.PWMB = 5
        self.BIN1 = 3
        self.BIN2 = 4
        self.pwm = PCA9685(0x40, debug=False)
        self.pwm.setPWMFreq(50)
        self.max_speed = max_speed
        self.min_speed = min_speed

    def Run(self, motor, direction, speed):
        if speed > 100 or speed < 0:
            raise Exception("Speed must be between 0 and 100")
        if direction not in ['forward', 'backward']:
            raise Exception("Direction must be 'forward' or 'backward'")
        if motor not in ['left', 'right']:
            raise Exception("Motor must be 'left' or 'right'")
        # scale speed to the range between min_speed and max_speed
        speed = int(((speed / 100) * (self.max_speed - self.min_speed) + self.min_speed) * 100)
        if(motor == 'left'):
            self.pwm.setDutycycle(self.PWMA, speed)
            if(direction == 'forward'):
                self.pwm.setLevel(self.AIN1, 0)
                self.pwm.setLevel(self.AIN2, 1)
            elif(direction == 'backward'):
                self.pwm.setLevel(self.AIN1, 1)
                self.pwm.setLevel(self.AIN2, 0)
        elif(motor == 'right'):
            self.pwm.setDutycycle(self.PWMB, speed)
            if (direction == 'forward'):
                self.pwm.setLevel(self.BIN1, 0)
                self.pwm.setLevel(self.BIN2, 1)
            elif (direction == 'backward'):
                self.pwm.setLevel(self.BIN1, 1)
                self.pwm.setLevel(self.BIN2, 0)

    def Stop(self, motor):
        if motor not in ['left', 'right']:
            raise Exception("Motor must be 'left' or 'right'")
        if (motor == 'left'):
            self.pwm.setDutycycle(self.PWMA, 0)
        elif (motor == 'right'):
            self.pwm.setDutycycle(self.PWMB, 1)
