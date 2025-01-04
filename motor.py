from asyncio import wait_for

from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
import uvicorn
import os
import json
from MotorControl import MotorControl
import multiprocessing


class MotorControlService:
    def __init__(self):
        self.motor_control = MotorControl()

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

    def handle_message(self, msg):
        try:
            event = json.loads(msg)
            match event["type"]:
                case "motorControl":
                    self.handle_motor_control_msg(event["params"])
                    return "ack"
        except Exception as e:
            print(f"Error in processing control message: {msg}, {e}")
            return "error"

class ControlWsState:
    def __init__(self):
        self.connected_clients_count = 0
        self.current_token = None

def async_ws_app(port, tokenQueue, controlQueue, motor_service):

    ws_app = FastAPI()

    ws_state = ControlWsState()

    def authorize(token):
        if not token:
            return False
        while not tokenQueue.empty():
            ws_state.current_token = tokenQueue.get()
            print(f"New token: {ws_state.current_token}")
        if ws_state.current_token and token == ws_state.current_token:
            return True
        else:
            return False

    @ws_app.websocket("/robotControlWs")
    async def websocket_endpoint(websocket: WebSocket, token: str = None):
        if not authorize(token):
            await websocket.close()
            return
        if ws_state.connected_clients_count > 0:
            await websocket.close()
            return
        await websocket.accept()
        ws_state.connected_clients_count += 1
        controlQueue.put(ws_state)
        print(f"WS Client connected")
        try:
            while True:
                try:
                    msg = await wait_for(websocket.receive_text(), timeout=0.5)
                except TimeoutError:
                    print("Timeout, stopping motors")
                    #motor_service.motor_control.Stop("left")
                    #motor_service.motor_control.Stop("right")
                #response = motor_service.handle_message(msg)
                print(f"Received message: {msg}")
                if msg == "pingMsg":
                    await websocket.send_text("pongMsg")
                else:
                    await websocket.send_text("ack")
        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            try:
                await websocket.close()
            except Exception as e:
                print(f"WS already closed")
            #motor_service.motor_control.Stop("left")
            #motor_service.motor_control.Stop("right")
            print(f"Client disconnected")
            ws_state.connected_clients_count -= 1
            ws_state.current_token = None
            controlQueue.put(ws_state)


    uvicorn.run(ws_app, host="0.0.0.0", port=port)


def async_rest_app(port, tokenQueue, controlQueue):
    rest_app = FastAPI()
    control_ws_state = ControlWsState()

    def get_latest_control_state():
        control_state = None
        while not controlQueue.empty():
            control_state = controlQueue.get()
        if control_state:
            control_ws_state.current_token = control_state.current_token
            control_ws_state.connected_clients_count = control_state.connected_clients_count

    @rest_app.get("/status")
    async def get_status():
        get_latest_control_state()
        return JSONResponse(content={"status": "active", "clients": control_ws_state.connected_clients_count})


    @rest_app.post("/startControlSession")
    async def start_control_session():
        get_latest_control_state()
        if control_ws_state.connected_clients_count > 0:
            return JSONResponse(content={"message": "Control session already active"}, status_code=400)
        token = os.urandom(16).hex()
        tokenQueue.put(token)
        return JSONResponse(content={"token": token, "wsPort": os.getenv("MOTOR_SERVICE_EXT_WS_PORT", 8080)})

    uvicorn.run(rest_app, host="127.0.0.1", port=port)

if __name__ == "__main__":

    tokens = multiprocessing.Queue()
    control_ws_state = multiprocessing.Queue()

    ws_port = os.getenv("MOTOR_SERVICE_EXT_WS_PORT", 8080)
    rest_port = os.getenv("MOTOR_SERVICE_INT_REST_PORT", 8081)

    ws_process = multiprocessing.Process(target=async_ws_app, args=(ws_port, tokens, control_ws_state, None))
    rest_process = multiprocessing.Process(target=async_rest_app, args=(rest_port, tokens, control_ws_state))

    ws_process.start()
    rest_process.start()

    ws_process.join()
    rest_process.join()