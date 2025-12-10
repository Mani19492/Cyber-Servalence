import asyncio
import cv2
import numpy as np
from collections import defaultdict

_latest = defaultdict(lambda: None)

def update_frame(camera_id: str, frame):
    """Update the latest frame for a camera"""
    try:
        _, jpg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        _latest[camera_id] = jpg.tobytes()
    except Exception as e:
        print(f"Error encoding frame for {camera_id}: {e}")

async def mjpeg_stream_generator(camera_id: str):
    """Generate MJPEG stream for a camera"""
    boundary = b"--frame"
    no_frame_count = 0
    
    while True:
        frame = _latest.get(camera_id)
        if frame:
            no_frame_count = 0
            yield (
                boundary
                + b"\r\nContent-Type: image/jpeg\r\nContent-Length: "
                + str(len(frame)).encode()
                + b"\r\n\r\n"
                + frame
                + b"\r\n"
            )
            await asyncio.sleep(0.033)  # ~30 FPS
        else:
            no_frame_count += 1
            # If no frame for 5 seconds, create placeholder
            if no_frame_count > 150:
                placeholder = create_placeholder_frame(camera_id)
                yield (
                    boundary
                    + b"\r\nContent-Type: image/jpeg\r\nContent-Length: "
                    + str(len(placeholder)).encode()
                    + b"\r\n\r\n"
                    + placeholder
                    + b"\r\n"
                )
            await asyncio.sleep(0.1)

def create_placeholder_frame(camera_id: str):
    """Create a placeholder frame when camera is not available"""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    text = f"Camera {camera_id} - Waiting for feed..."
    cv2.putText(frame, text, (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    _, jpg = cv2.imencode(".jpg", frame)
    return jpg.tobytes()

def stream_mjpeg(url: str):
    """Legacy function for backward compatibility"""
    return mjpeg_stream_generator("default")
