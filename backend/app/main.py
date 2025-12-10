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
    password = data.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")

    db_user = get_user_by_email(email)

    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")

    # Database uses hashed_password instead of password
    stored_password = db_user.get("hashed_password") or db_user.get("password")
    if not stored_password:
        raise HTTPException(status_code=401, detail="Invalid user data - no password found")

    # Debug logging
    print(f"Login attempt for: {email}")
    print(f"Stored password hash: {stored_password[:20]}...")
    
    try:
        if not verify_password(password, stored_password):
            print("Password verification failed")
            raise HTTPException(status_code=401, detail="Invalid password")
    except Exception as e:
        print(f"Password verification error: {e}")
        raise HTTPException(status_code=401, detail=f"Invalid password: {str(e)}")

    token = create_jwt_token(email)
    return {"access_token": token, "token_type": "bearer"}

# ---------------- ADMIN CREATE ------------------

@app.post("/admin/init")
def init_admin():
    """Initialize admin user if it doesn't exist"""
    existing_user = get_user_by_email(settings.admin_email)
    if existing_user:
        return {"message": "Admin already exists", "email": settings.admin_email}
    
    hashed = hash_password(settings.admin_password)
    create_user(settings.admin_email, hashed)
    return {
        "message": "Admin created",
        "email": settings.admin_email,
        "password_hash": hashed[:30] + "..."
    }

@app.get("/debug/user/{email}")
def debug_user(email: str):
    """Debug endpoint to check user in database"""
    user = get_user_by_email(email)
    if not user:
        return {"found": False, "email": email}
    
    return {
        "found": True,
        "email": user.get("email"),
        "has_password": bool(user.get("hashed_password") or user.get("password")),
        "hashed_password_preview": (user.get("hashed_password") or user.get("password") or "")[:50] + "..." if (user.get("hashed_password") or user.get("password")) else None,
        "role": user.get("role"),
        "all_fields": list(user.keys())
    }

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
