from gpiozero import Motor, PWMOutputDevice
from time import sleep

motLeft = Motor(24, 23)
motLeftPWM = PWMOutputDevice(pin=25, initial_value=0.7)
motRight = Motor(20, 21)
motRightPWM = PWMOutputDevice(pin=12, initial_value=0.7)

def motorTest():
    motRight.forward()
    motLeft.forward()
    sleep(1.5)
    motRight.backward()
    motLeft.backward()
    sleep(1.5)
    motRight.stop()
    motLeft.stop()

import asyncio
from websockets.server import serve

async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)

async def main():
    async with serve(echo, "", 8000):
        await asyncio.Future() 

asyncio.run(main())
