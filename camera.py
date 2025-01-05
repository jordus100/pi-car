from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
import asyncio
from datetime import datetime
import os
from typing import Optional

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
    def __init__(self, photo_interval: 30):
        self.camera = None
        self.output = None
        self.photo_task: Optional[asyncio.Task] = None
        self.photo_interval = photo_interval

    async def start_camera(self):
        if self.camera is None:
            self.camera = Picamera2()
            self.camera.configure(self.camera.create_video_configuration(main={"size": (1640, 1232)}))
            self.output = AsyncStreamingOutput()
            self.camera.start_recording(JpegEncoder(), FileOutput(self.output))
            print("Camera started")

    async def stop_camera(self):
        if self.camera:
            self.camera.stop_recording()
            self.camera.close()
            self.camera = None
            self.output = None
            print("Camera stopped")

    def start_photo_task(self):
        if not self.photo_task or self.photo_task.done():
            self.photo_task = asyncio.create_task(self.capture_photos())

    def stop_photo_task(self):
        if self.photo_task and not self.photo_task.done():
            self.photo_task.cancel()
            print("Photo capture task stopped")

    async def capture_photos(self):
        """Background task to take still photos at regular intervals."""
        await self.start_camera()
        while True:
            try:
                if self.camera:
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

camera_manager = CameraManager()

@asynccontextmanager
async def camera_lifespan(app):
    camera_manager.start_photo_task()
    yield
    camera_manager.stop_photo_task()

app = FastAPI(lifespan=camera_lifespan)

async def mjpeg_stream():
    boundary = b"--FRAME\r\n"
    try:
        await camera_manager.start_camera()
        while True:
            frame = await camera_manager.output.get_frame()
            yield boundary
            yield b"Content-Type: image/jpeg\r\n"
            yield f"Content-Length: {len(frame)}\r\n\r\n".encode()
            yield frame
            yield b"\r\n"
    except asyncio.CancelledError:
        print("Streaming stopped by client")

@app.get("/stream.mjpg")
async def get_stream():
    if camera_manager.camera is None:
        raise HTTPException(status_code=500, detail="Camera not initialized")
    return StreamingResponse(mjpeg_stream(), media_type="multipart/x-mixed-replace; boundary=FRAME")

@app.get("/")
async def root():
    return {"message": "Welcome to the MJPEG streaming server!"}