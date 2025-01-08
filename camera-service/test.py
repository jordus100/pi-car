import asyncio
import os
import cv2
import numpy as np
import uvicorn

from camera_manager import CameraManager, AsyncStreamingOutput
from camera_app import camera_streaming_app

class MockCamera:
    def __init__(self):
        self.recording = False
        self.output = None

    def configure(self, config):
        pass

    def create_video_configuration(self, **kwargs):
        pass

    def set_controls(self, config):
        pass

    def start_recording(self, output):
        self.recording = True
        self.output = output
        asyncio.create_task(self._generate_frames())

    def stop_recording(self):
        self.recording = False

    def close(self):
        pass

    def capture_file(self, filepath):
        pass

    async def _generate_frames(self):
        while self.recording:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            col = np.random.randint(0, 255, 3)
            frame[:] = col
            _, buffer = cv2.imencode('.jpg', frame)
            self.output.write(buffer.tobytes())
            await asyncio.sleep(0.1)

if __name__ == "__main__":
    camera = MockCamera()
    camera_manager = CameraManager(camera)
    auth_url = os.getenv("AUTHENTICATION_URL", "http://localhost:5000/api/auth")
    camera_app = camera_streaming_app(camera_manager, auth_url)
    camera_port = int(os.getenv("CAMERA_SERVICE_EXT_PORT", 8000))
    uvicorn.run(camera_app, host="0.0.0.0", port=camera_port)
