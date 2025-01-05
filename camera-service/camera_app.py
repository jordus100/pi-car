import asyncio
import httpx
from fastapi import Request, HTTPException

from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.responses import StreamingResponse


def camera_streaming_app(camera_manager, authentication_url):

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
            camera_manager.stream_clients -= 1
            print(f"Client disconnected, active clients: {camera_manager.stream_clients}")
            if camera_manager.stream_clients == 0:
                await camera_manager.stop_recording()

    async def authenticate_via_flask(request: Request):
        cookies = request.cookies
        async with httpx.AsyncClient() as client:
            response = await client.get(authentication_url, cookies=cookies)
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Authentication failed")

    @app.get("/stream.mjpg")
    async def get_stream(request: Request):
        await authenticate_via_flask(request)
        camera_manager.stream_clients += 1
        print(f"New client connected, active clients: {camera_manager.stream_clients}")
        return StreamingResponse(mjpeg_stream(), media_type="multipart/x-mixed-replace; boundary=FRAME")

    @app.get("/")
    async def root():
        return {"message": "Welcome to the MJPEG streaming server!"}

    return app
