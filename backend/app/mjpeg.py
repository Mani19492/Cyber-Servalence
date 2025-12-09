import asyncio
import cv2
from collections import defaultdict

_latest = defaultdict(lambda: None)

def update_frame(camera_id: str, frame):
    _, jpg = cv2.imencode(".jpg", frame)
    _latest[camera_id] = jpg.tobytes()

async def mjpeg_stream_generator(camera_id: str):
    boundary = b"--frame"
    while True:
        frame = _latest.get(camera_id)
        if frame:
            yield (
                boundary
                + b"\r\nContent-Type: image/jpeg\r\nContent-Length: "
                + str(len(frame)).encode()
                + b"\r\n\r\n"
                + frame
                + b"\r\n"
            )
        await asyncio.sleep(0.05)
