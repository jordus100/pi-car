#!/home/pi/dyplom/venv2/bin/python
from gpiozero import Motor, PWMOutputDevice
from time import sleep
import os

from PCA9685 import PCA9685
import time

Dir = [
    'forward',
    'backward',
]
pwm = PCA9685(0x40, debug=False)
pwm.setPWMFreq(50)

class Motor_Driver():
    def __init__(self):
        self.PWMA = 0
        self.AIN1 = 1
        self.AIN2 = 2
        self.PWMB = 5
        self.BIN1 = 3
        self.BIN2 = 4

    def Run(self, motor, index, speed):
        if speed > 100:
            return
        if(motor == 0):
            pwm.setDutycycle(self.PWMA, speed)
            if(index == Dir[0]):
                print ("1")
                pwm.setLevel(self.AIN1, 0)
                pwm.setLevel(self.AIN2, 1)
            else:
                print ("2")
                pwm.setLevel(self.AIN1, 1)
                pwm.setLevel(self.AIN2, 0)
        else:
            pwm.setDutycycle(self.PWMB, speed)
            if(index == Dir[0]):
                print ("3")
                pwm.setLevel(self.BIN1, 0)
                pwm.setLevel(self.BIN2, 1)
            else:
                print ("4")
                pwm.setLevel(self.BIN1, 1)
                pwm.setLevel(self.BIN2, 0)

    def Stop(self, motor):
        if (motor == 0):
            pwm.setDutycycle(self.PWMA, 0)
        else:
            pwm.setDutycycle(self.PWMB, 0)

Motors = Motor_Driver()

MIN_POWER = 0.7

motLeft = 0
motRight = 1

def motorTest():
    motRight.forward()
    motLeft.forward()
    sleep(1.5)
    motRight.backward()
    motLeft.backward()
    sleep(1.5)
    motRight.stop()
    motLeft.stop()

def stopMotors():
    Motors.Stop(0)
    Motors.Stop(1)

def handleMotorAction(params, motor):
    match params["action"]:
        case "stop":
            Motors.Stop(motor)
        case "drive":
            thrust = params["thrust"]
            direction = 'forward'
            if thrust < 0:
                direction = 'backward'
            scaledThrust = 0
            if thrust != 0:
                scaledThrust = int(((abs(thrust) / 100) * (1.0 - MIN_POWER) + MIN_POWER) * 100)
                print(scaledThrust)
            Motors.Run(motor, direction, scaledThrust)

def handleMotorControlMsg(params):
    leftMot = params["leftMotor"]
    rightMot = params["rightMotor"]
    handleMotorAction(leftMot, motLeft)
    handleMotorAction(rightMot, motRight)

import asyncio
from websockets.server import serve
import json

def handleMessage(msg):
    print(msg)
    try:
        if msg == "shutdown":
            stopMotors()
            os.system("sudo shutdown -h now")
            return
        event = json.loads(msg)
        match event["type"]:
            case "motorControl":
                handleMotorControlMsg(event["params"])
        return "ack"
    except:
        print("Error in processing control message", msg)

async def echo(websocket):
    print("CONNECTED")
    try:
        async for msg in websocket:
            returnMsg = handleMessage(msg)
            await websocket.send(returnMsg)
            
    finally:
        print("DISCONNECTED")
        stopMotors()

async def main():
    async with serve(echo, "", 8000, ping_interval=1, ping_timeout=1):
        await asyncio.Future() 

asyncio.run(main())
