import uvicorn
import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from websocket_app import ControlWsState


def async_rest_app(port, tokenQueue, controlQueue):
    rest_app = FastAPI()
    control_ws_state = ControlWsState()

    def get_latest_control_state():
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
