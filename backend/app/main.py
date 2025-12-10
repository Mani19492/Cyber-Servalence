from fastapi import FastAPI, UploadFile, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .config import settings
from .db import *
from .face import extract_face_embedding
from .mjpeg import mjpeg_stream_generator, update_frame
from .utils import create_jwt_token, verify_password, hash_password, verify_jwt_token
from .camera_worker import CameraWorker
from .models import Token
import cv2
import numpy as np
import json
from typing import Dict, List
import asyncio
from datetime import datetime

app = FastAPI(title="Cyber Servalence API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Store active camera workers
active_workers: Dict[str, CameraWorker] = {}

# Store WebSocket connections
websocket_connections: List[WebSocket] = []

# Broadcast alert to all connected WebSocket clients
async def broadcast_alert(alert_data: dict):
    disconnected = []
    for ws in websocket_connections:
        try:
            await ws.send_json({"type": "detection", "data": alert_data})
        except:
            disconnected.append(ws)
    
    # Remove disconnected clients
    for ws in disconnected:
        if ws in websocket_connections:
            websocket_connections.remove(ws)

# ---------------- LOGIN ------------------

@app.post("/login", response_model=Token)
@app.post("/auth/login", response_model=Token)
def login(data: dict):
    email = data.get("email") or data.get("username")

    if not email:
        raise HTTPException(status_code=400, detail="Email/username required")

    # FAKE LOGIN - Allow any email to login without database check
    print(f"Fake login successful for: {email} (no database check)")
    token = create_jwt_token(email)
    return {"access_token": token, "token_type": "bearer"}

# ---------------- ADMIN CREATE ------------------

@app.post("/admin/init")
def init_admin():
    """Initialize admin user if it doesn't exist"""
    try:
        existing_user = get_user_by_email(settings.admin_email)
        if existing_user:
            return {
                "message": "Admin already exists", 
                "email": settings.admin_email,
                "login": "Just login with email: " + settings.admin_email
            }
        
        # Create admin user (no password needed)
        print(f"Creating admin user: {settings.admin_email}")
        create_user(settings.admin_email, "")  # Empty password since we don't use it
        
        # Verify it was created
        verify_user = get_user_by_email(settings.admin_email)
        return {
            "message": "Admin created",
            "email": settings.admin_email,
            "verified": bool(verify_user),
            "login": "Just login with email: " + settings.admin_email + " (no password needed)"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "type": type(e).__name__,
            "message": "Failed to create admin user"
        }

@app.get("/debug/user/{email}")
def debug_user(email: str):
    """Debug endpoint to check user in database"""
    try:
        user = get_user_by_email(email)
        if not user:
            return {"found": False, "email": email}
        
        stored_password = user.get("password") or user.get("hashed_password")
        
        return {
            "found": True,
            "email": user.get("email"),
            "has_password": bool(stored_password),
            "password_preview": stored_password[:10] + "..." if stored_password else None,
            "password_is_plain_text": not (stored_password and stored_password.startswith("$2b$")) if stored_password else None,
            "password_length": len(stored_password) if stored_password else 0,
            "role": user.get("role"),
            "all_fields": list(user.keys()),
            "note": "Using plain text passwords (not secure for production!)"
        }
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

# ---------------- WEBSOCKET ALERTS ------------------

@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        while True:
            # Keep connection alive
            await asyncio.sleep(1)
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)

# ---------------- CAMERAS ENDPOINTS ------------------

@app.get("/api/cameras")
@app.get("/cameras")
def get_cameras():
    try:
        cameras = get_all_cameras()
        return cameras or []
    except Exception as e:
        return []

@app.post("/api/cameras")
def add_camera(data: dict):
    cam_id = data.get("id")
    url = data.get("url") or data.get("rtsp_url")
    name = data.get("name") or data.get("location", f"Camera {cam_id}")
    
    if not cam_id or not url:
        raise HTTPException(status_code=400, detail="Camera ID and URL required")
    
    # Insert camera with cam_id as TEXT primary key
    insert_camera(name, url, cam_id)
    
    # Start camera worker
    if cam_id not in active_workers:
        worker = CameraWorker(cam_id, url, broadcast_alert)
        active_workers[cam_id] = worker
        worker.start()
    
    return {"message": "Camera added", "id": cam_id}

# ---------------- STREAM ENDPOINT ------------------

@app.get("/stream/{camera_id}")
async def camera_stream(camera_id: str):
    return StreamingResponse(
        mjpeg_stream_generator(camera_id),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/snapshots/{filename}")
async def get_snapshot(filename: str):
    from fastapi.responses import FileResponse
    import os
    filepath = os.path.join("snapshots", filename)
    if os.path.exists(filepath):
        return FileResponse(filepath, media_type="image/jpeg")
    raise HTTPException(status_code=404, detail="Snapshot not found")

# --------------- ADD PERSON ----------------

@app.post("/persons/add")
async def add_person(name: str, file: UploadFile):
    img = cv2.imdecode(np.frombuffer(await file.read(), np.uint8), cv2.IMREAD_COLOR)

    emb = extract_face_embedding(img)
    if emb is None:
        raise HTTPException(status_code=400, detail="No face found")

    insert_person(name, emb)
    return {"message": "Person added"}

# --------------- MJPEG CAMERA STREAM (legacy) ----------------

@app.get("/camera/stream")
def camera_stream_legacy(url: str):
    return StreamingResponse(
        mjpeg_stream_generator("default"),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.on_event("startup")
async def startup_event():
    """Initialize cameras on startup"""
    try:
        cameras = get_all_cameras()
        for cam in cameras:
            cam_id = str(cam.get("id", cam.get("name", "unknown")))
            # Get url from either url or rtsp_url field
            url = cam.get("url") or cam.get("rtsp_url")
            if url:
                if cam_id not in active_workers:
                    worker = CameraWorker(cam_id, url, broadcast_alert)
                    active_workers[cam_id] = worker
                    worker.start()
    except Exception as e:
        print(f"Error initializing cameras: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Stop all camera workers on shutdown"""
    for worker in active_workers.values():
        worker.running = False
    active_workers.clear()
