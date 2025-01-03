#!/home/pi/dyplom/venv2/bin/python
from time import sleep
import os
import asyncio
from websockets.server import serve
import json

import MotorControl

class MotorControlWS:
    def __init__(self, port=8000, motorControl=MotorControl()):
        self.motorControl = motorControl
        self.port = port
        asyncio.run(self.serve_ws())

    def handleMotorAction(self, params, motor):
        match params["action"]:
            case "stop":
                self.motorControl.Stop(motor)
            case "drive":
                thrust = params["thrust"]
                direction = 'forward'
                if thrust < 0:
                    direction = 'backward'
                self.motorControl.Run(motor, direction, thrust)

    def handleMotorControlMsg(self, params):
        leftMot = params["leftMotor"]
        rightMot = params["rightMotor"]
        self.handleMotorAction(leftMot, "left")
        self.handleMotorAction(rightMot, "right")

    def handleMessage(self, msg):
        print(msg)
        try:
            if msg == "shutdown":
                MotorControl.Stop("left")
                MotorControl.Stop("right")
                os.system("sudo shutdown -h now")
                return
            event = json.loads(msg)
            match event["type"]:
                case "motorControl":
                    self.handleMotorControlMsg(event["params"])
            return "ack"
        except:
            print("Error in processing control message", msg)

    async def echo(self, websocket):
        print("CONNECTED")
        try:
            async for msg in websocket:
                response = self.handleMessage(msg)
                await websocket.send(response)
        finally:
            print("DISCONNECTED")
            MotorControl.Stop("left")
            MotorControl.Stop("right")

    async def serve_ws(self):
        async with serve(self.echo, "", 8000, ping_interval=1, ping_timeout=1):
            await asyncio.Future()
