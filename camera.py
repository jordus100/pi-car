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
import uvicorn

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
        self.camera.configure(self.camera.create_video_configuration(main={"size": (1640, 1232)}))
        self.output = AsyncStreamingOutput()
        print("Camera initialized")

    async def start_recording(self):
        if self.camera and not self.camera.recording:
            self.camera.start_recording(JpegEncoder(), FileOutput(self.output))
            print("Camera recording started")

    async def stop_recording(self):
        if self.camera and self.camera.recording:
            self.camera.stop_recording()
            print("Camera recording stopped")

    async def close_camera(self):
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


def camera_streaming_app(camera_manager):

    @asynccontextmanager
    async def camera_lifespan(app):
        await camera_manager.initialize_camera()
        camera_manager.start_photo_task()
        yield
        camera_manager.stop_photo_task()
        await camera_manager.close_camera()

    app = FastAPI(lifespan=camera_lifespan)

    async def mjpeg_stream():
        boundary = b"--FRAME\r\n"
        try:
            await camera_manager.start_recording()
            while True:
                frame = await camera_manager.output.get_frame()
                yield boundary
                yield b"Content-Type: image/jpeg\r\n"
                yield f"Content-Length: {len(frame)}\r\n\r\n".encode()
                yield frame
                yield b"\r\n"
        except asyncio.CancelledError:
            print("Streaming stopped by client")
        finally:
            # Decrease the client count when a client disconnects
            camera_manager.stream_clients -= 1
            print(f"Client disconnected, active clients: {camera_manager.stream_clients}")
            if camera_manager.stream_clients == 0:
                await camera_manager.stop_recording()

    @app.get("/stream.mjpg")
    async def get_stream():
        # Increase the client count when a new client connects
        camera_manager.stream_clients += 1
        print(f"New client connected, active clients: {camera_manager.stream_clients}")
        return StreamingResponse(mjpeg_stream(), media_type="multipart/x-mixed-replace; boundary=FRAME")

    @app.get("/")
    async def root():
        return {"message": "Welcome to the MJPEG streaming server!"}

    return app

if __name__ == "__main__":
    camera = Picamera2()
    camera_manager = CameraManager(camera)
    camera_app = camera_streaming_app(camera_manager)
    camera_port = int(os.getenv("CAMERA_SERVICE_EXT_PORT", 8000))
    uvicorn.run(camera_app, host="0.0.0.0", port=camera_port)
