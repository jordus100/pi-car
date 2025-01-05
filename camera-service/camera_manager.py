import asyncio
import os
from datetime import datetime
from typing import Optional

#from picamera2.encoders import JpegEncoder
#from picamera2.outputs import FileOutput

PHOTO_SAVE_DIR = "photos"
os.makedirs(PHOTO_SAVE_DIR, exist_ok=True)

class AsyncStreamingOutput:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.latest_frame: Optional[bytes] = None

    async def write(self, buf):
        self.latest_frame = buf
        while not self.queue.empty():
            self.queue.get_nowait()
        await self.queue.put(buf)

    async def get_frame(self):
        return await self.queue.get()

class CameraManager:
    def __init__(self, camera, photo_interval: int = 30):
        self.camera = camera
        self.output = None
        self.photo_task: Optional[asyncio.Task] = None
        self.photo_interval = photo_interval
        self.stream_clients = 0  # Track active clients for streaming

    async def initialize_camera(self):
        """Initialize the camera for capturing photos."""
        self.camera.configure(self.camera.create_video_configuration(main={"size": (1640, 1232)}))
        self.output = AsyncStreamingOutput()
        print("Camera initialized")

    async def start_recording(self):
        """Start recording for streaming."""
        if self.camera and not self.camera.recording:
            #self.camera.start_recording(JpegEncoder(), FileOutput(self.output))
            self.camera.start_recording(None, self.output)
            print("Camera recording started")

    async def stop_recording(self):
        """Stop recording for streaming."""
        if self.camera and self.camera.recording:
            self.camera.stop_recording()
            print("Camera recording stopped")

    async def close_camera(self):
        """Close the camera completely."""
        if self.camera:
            if self.camera.recording:
                await self.stop_recording()
            self.camera.close()
            self.camera = None
            print("Camera closed")

    def start_photo_task(self):
        if not self.photo_task or self.photo_task.done():
            self.photo_task = asyncio.create_task(self.capture_photos())

    def stop_photo_task(self):
        if self.photo_task and not self.photo_task.done():
            self.photo_task.cancel()
            print("Photo capture task stopped")

    async def capture_photos(self):
        """Background task to take still photos at regular intervals."""
        while True:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = os.path.join(PHOTO_SAVE_DIR, f"{timestamp}.jpg")
                self.camera.capture_file(filepath)
                print(f"Photo captured: {filepath}")
                await asyncio.sleep(self.photo_interval)
            except asyncio.CancelledError:
                print("Photo capture task canceled")
                break
            except Exception as e:
                print(f"Error capturing photo: {e}")
