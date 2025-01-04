from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
import asyncio
from typing import Optional

app = FastAPI()

class AsyncStreamingOutput:
    """Asynchronous streaming output using asyncio.Queue."""
    def __init__(self):
        self.queue = asyncio.Queue()
        self.latest_frame: Optional[bytes] = None  # Store the latest frame for faster access

    async def write(self, buf):
        """Write a new frame to the queue."""
        self.latest_frame = buf
        # Clear the queue to ensure only the latest frame is available
        while not self.queue.empty():
            self.queue.get_nowait()
        await self.queue.put(buf)

    async def get_frame(self):
        """Retrieve the latest frame."""
        return await self.queue.get()

# Initialize the camera and asynchronous output
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (1640, 1232)}))
output = AsyncStreamingOutput()
picam2.start_recording(JpegEncoder(), FileOutput(output))

async def mjpeg_stream():
    """Generator to provide an MJPEG stream asynchronously."""
    boundary = b"--FRAME\r\n"
    try:
        while True:
            frame = await output.get_frame()
            yield boundary
            yield b"Content-Type: image/jpeg\r\n"
            yield f"Content-Length: {len(frame)}\r\n\r\n".encode()
            yield frame
            yield b"\r\n"
    except asyncio.CancelledError:
        print("Streaming stopped by client")
    except Exception as e:
        print(f"Streaming stopped due to error: {e}")

@app.get("/stream.mjpg")
async def get_stream():
    """Serve the MJPEG stream."""
    return StreamingResponse(mjpeg_stream(), media_type="multipart/x-mixed-replace; boundary=FRAME")

@app.get("/")
async def root():
    """Simple endpoint to test the server."""
    return {"message": "Welcome to the MJPEG streaming server!"}