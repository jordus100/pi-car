#!/home/pi/dyplom/venv/bin/python
from gpiozero import Motor, PWMOutputDevice
from time import sleep
import os

MIN_POWER = 0.7

motLeft = Motor(24, 23)
motLeftPWM = PWMOutputDevice(pin=25, initial_value=0.0)
motRight = Motor(20, 21)
motRightPWM = PWMOutputDevice(pin=12, initial_value=0.0)

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
    motRight.stop()
    motLeft.stop()

def handleMotorAction(params, motor, motPWM):
    match params["action"]:
        case "stop":
            motor.stop()
        case "drive":
            thrust = params["thrust"]
            if thrust >= 0:
                motor.forward()
            else:
                motor.backward()
            scaledThrust = 0.0
            if thrust != 0:
                scaledThrust = (abs(thrust) / 100) * (1.0 - MIN_POWER) + MIN_POWER
            motPWM.value = scaledThrust

def handleMotorControlMsg(params):
    global motLeft, motRight, motLeftPWM, motRightPWM
    leftMot = params["leftMotor"]
    rightMot = params["rightMotor"]
    handleMotorAction(leftMot, motLeft, motLeftPWM)
    handleMotorAction(rightMot, motRight, motRightPWM)

import asyncio
from websockets.server import serve
import json

def handleMessage(msg):
    print(msg)
    try:
        event = json.loads(msg)
        match event["type"]:
            case "motorControl":
                handleMotorControlMsg(event["params"])
        return "ack"
    except:
        if msg == "shutdown":
            os.system("sudo shutdown -h now")

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
