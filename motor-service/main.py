import multiprocessing
import os
from websocket_app import async_ws_app
from rest_app import async_rest_app

if __name__ == "__main__":
    tokens = multiprocessing.Queue()
    control_ws_state = multiprocessing.Queue()

    ws_port = int(os.getenv("MOTOR_SERVICE_EXT_WS_PORT", 8080))
    rest_port = int(os.getenv("MOTOR_SERVICE_INT_REST_PORT", 8081))

    ws_process = multiprocessing.Process(target=async_ws_app, args=(ws_port, tokens, control_ws_state, None))
    rest_process = multiprocessing.Process(target=async_rest_app, args=(rest_port, tokens, control_ws_state))

    ws_process.start()
    rest_process.start()

    ws_process.join()
    rest_process.join()
