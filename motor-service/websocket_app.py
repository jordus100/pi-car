import uvicorn
from fastapi import FastAPI, WebSocket
from asyncio import wait_for, TimeoutError


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
                    #motor_service.stopMotors()
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
            # motor_service.stopMotors()
            print(f"Client disconnected")
            ws_state.connected_clients_count -= 1
            ws_state.current_token = None
            controlQueue.put(ws_state)


    uvicorn.run(ws_app, host="0.0.0.0", port=port)
