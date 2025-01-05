import os
import uvicorn
from picamera2 import Picamera2

from camera_manager import CameraManager
from camera_app import camera_streaming_app

if __name__ == "__main__":
    camera = Picamera2()
    camera_manager = CameraManager(camera)
    camera_app = camera_streaming_app(camera_manager)
    camera_port = int(os.getenv("CAMERA_SERVICE_EXT_PORT", 8000))
    uvicorn.run(camera_app, host="0.0.0.0", port=camera_port)
