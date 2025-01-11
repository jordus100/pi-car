import io
import asyncio
import os
from datetime import datetime
from typing import Optional
from queue import Queue

# from picamera2.encoders import JpegEncoder
# from picamera2.outputs import FileOutput

PHOTO_SAVE_DIR = "photos"
os.makedirs(PHOTO_SAVE_DIR, exist_ok=True)

class AsyncStreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.latest_frame: Optional[bytes] = None
        self.queues = []

    def write(self, buf):
        self.latest_frame = buf
        for queue in self.queues:
            queue.put(buf)

    def subscribe(self, clientQueue):
        self.queues.append(clientQueue)

    def unsubscribe(self, clientQueue):
        self.queues.remove(clientQueue)
    

class CameraManager:
    def __init__(self, camera, photo_interval: int = 30):
        self.camera = camera
        self.output = None
        self.photo_task: Optional[asyncio.Task] = None
        self.photo_interval = photo_interval
        self.stream_clients = 0  # Track active clients for streaming
        self.recording = False
        self.streaming = False

    async def initialize_camera(self):
        """Initialize the camera for capturing photos."""
        self.camera.configure(self.camera.create_video_configuration(main={"size": (640, 480)}))
        self.camera.set_controls({"FrameRate": 4})
        self.output = AsyncStreamingOutput()
        print("Camera initialized")

    async def start_recording(self, purpose=None):
        """Start recording for streaming."""
        if self.camera and not self.recording:
            #self.camera.start_recording(JpegEncoder(), FileOutput(self.output))
            self.camera.start_recording(self.output)
            self.recording = True
            if purpose == 'streaming':
                self.streaming = True
            print("Camera recording started")
        return self.output

    async def stop_recording(self, purpose=None):
        """Stop recording for streaming."""
        if self.camera and self.recording:
            self.camera.stop_recording()
            self.recording = False
            print("Camera recording stopped")
        if purpose == 'streaming':
            self.streaming = False

    async def close_camera(self):
        """Close the camera completely."""
        if self.camera:
            if self.recording:
                await self.stop_recording()
            self.camera.close()
            self.recording = False
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
                await self.start_recording()
                await asyncio.sleep(3)
                with open(filepath, "wb") as f:
                    print(self.output.latest_frame[5000])
                    f.write(self.output.latest_frame)
                if not self.streaming:
                    await self.stop_recording()
                #self.camera.switch_mode_and_capture_file(config, filepath)
                print(f"Photo captured: {filepath}")
                await asyncio.sleep(self.photo_interval)
            except asyncio.CancelledError:
                print("Photo capture task canceled")
                break
            except Exception as e:
                print(f"Error capturing photo: {e}")
