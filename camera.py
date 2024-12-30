#!/usr/bin/python3

import io
import logging
import socketserver
from http import server
from threading import Condition

from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
from libcamera import Transform

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


class StreamingHandler(server.BaseHTTPRequestHandler):
    def __init__(self, *args, output=None, **kwargs):
            self.output = output  # Store output explicitly in the handler instance
            super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, server_address, RequestHandlerClass, output):
            self.output = output  # Store output explicitly in the server
            super().__init__(server_address, RequestHandlerClass)

    def finish_request(self, request, client_address):
        """Override this method to pass output to the request handler"""
        self.RequestHandlerClass(request, client_address, self, output=self.output)

picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (1640, 1232)}))
#picam2.configure(picam2.create_video_configuration(main={"size": (1640, 1232)}, transform=Transform(hflip=True, vflip=True)))
output = StreamingOutput()
picam2.start_recording(JpegEncoder(), FileOutput(output))

try:
    address = ('', 9000)
    server = StreamingServer(address, StreamingHandler, output=output)
    server.serve_forever()
finally:
    picam2.stop_recording()
