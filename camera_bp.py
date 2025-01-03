import io
import logging
from threading import Condition
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
from flask import Blueprint, Response

# Camera streaming setup
class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

# Set up the camera and output
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (1640, 1232)}))
output = StreamingOutput()
picam2.start_recording(JpegEncoder(), FileOutput(output))

# Blueprint for streaming
camera_bp = Blueprint('camera', __name__)

@camera_bp.route('/stream.mjpg')
def stream_video():
    def generate():
        """Generate MJPEG stream."""
        try:
            while True:
                with output.condition:
                    output.condition.wait()
                    frame = output.frame
                yield (b'--FRAME\r\n'
                       b'Content-Type: image/jpeg\r\n'
                       b'Content-Length: ' + str(len(frame)).encode() + b'\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            logging.warning(f"Streaming error: {e}")

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=FRAME')

# Stop camera recording when the application shuts down
def stop_camera():
    picam2.stop_recording()
