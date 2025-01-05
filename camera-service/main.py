import os
import uvicorn
from picamera2 import Picamera2

from camera_manager import CameraManager
from camera_app import camera_streaming_app

if __name__ == "__main__":
    camera = Picamera2()
    camera_manager = CameraManager(camera)
    auth_url = os.getenv("AUTHENTICATION_URL", "http://localhost:5000/api/auth")
    camera_app = camera_streaming_app(camera_manager, auth_url)
    camera_port = int(os.getenv("CAMERA_SERVICE_EXT_PORT", 8000))
    uvicorn.run(camera_app, host="0.0.0.0", port=camera_port)
