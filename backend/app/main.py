"""
FastAPI app (GPU-ready).
- Auth: JWT (simple)
- Persons upload endpoint (operator)
- Add camera endpoint (operator) which starts camera_loop
- WS alerts
- MJPEG stream endpoint
"""

import uvicorn
import asyncio
import numpy as np
import cv2
from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from .config import settings
from .db import supabase, insert_person, get_all_persons, insert_camera, get_all_cameras, insert_detection, get_user_by_email, create_user
from .utils import encrypt_embedding, create_access_token, hash_password, verify_password, get_current_user, require_role
from .face import get_face_analyzer, detect_faces, get_embedding_from_face
from .camera_worker import camera_loop, ALERT_CALLBACK
from .mjpeg import mjpeg_stream_generator, update_frame

app = FastAPI(title="Cyber Servalence - GPU Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

# WebSocket manager
class WSManager:
    def __init__(self):
        self.clients: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.clients.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.clients:
            self.clients.remove(ws)

    async def broadcast(self, msg: dict):
        dead = []
        for c in list(self.clients):
            try:
                await c.send_json(msg)
            except:
                dead.append(c)
        for d in dead:
            try:
                self.clients.remove(d)
            except:
                pass

manager = WSManager()

# wire camera worker callback
async def alert_cb(alert: dict):
    await manager.broadcast({"type":"detection", "data": alert})

import app.camera_worker as cw
cw.ALERT_CALLBACK = alert_cb

# ========== AUTH (simple) ==========

@app.post("/auth/register")
def register(email: str, password: str, role: str = "viewer"):
    # WARNING: for prod require admin-only register
    if get_user_by_email(email):
        raise HTTPException(status_code=400, detail="already exists")
    hashed = hash_password(password)
    user = create_user(email, hashed, role)
    return {"id": user["id"], "email": user["email"], "role": user["role"]}

@app.post("/auth/login")
def login(username: str, password: str):
    user = get_user_by_email(username)
    if not user or not verify_password(password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user["email"]})
    return {"access_token": token, "token_type": "bearer"}

# ========== Persons ==========

@app.post("/api/persons")
async def add_person(file: UploadFile = File(...), name: str = "", metadata: str = "{}", user=Depends(require_role("operator"))):
    contents = await file.read()
    arr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return JSONResponse({"error":"invalid image"}, status_code=400)
    # get embedding
    try:
        emb = get_embedding_from_face(img)
    except Exception as e:
        return JSONResponse({"error":"could not extract embedding", "detail": str(e)}, status_code=500)
    enc = encrypt_embedding(emb)
    import json
    m = {}
    try:
        m = json.loads(metadata)
    except:
        m = {}
    row = insert_person(name, m, enc)
    return {"status":"ok", "person": row}

@app.get("/api/persons")
def persons_list(user=Depends(get_current_user)):
    return get_all_persons()

# ========== Cameras ==========

@app.post("/api/cameras")
async def add_camera_endpoint(id: str, rtsp_url: str, location: str = "", user=Depends(require_role("operator"))):
    # store in DB
    row = insert_camera(id, rtsp_url, location, {})
    # start camera worker async
    asyncio.ensure_future(camera_loop(id, rtsp_url))
    return {"status": "started", "camera": row}

@app.get("/api/cameras")
def list_cameras(user=Depends(get_current_user)):
    return get_all_cameras()

# MJPEG stream
@app.get("/stream/{camera_id}")
def stream(camera_id: str):
    return StreamingResponse(mjpeg_stream_generator(camera_id), media_type="multipart/x-mixed-replace; boundary=--frame")

# snapshots
@app.get("/snapshots/{fname}")
def get_snapshot(fname: str):
    p = f"snapshots/{fname}"
    if not os.path.exists(p):
        return JSONResponse({"error":"not found"}, status_code=404)
    return FileResponse(p)

# WS alerts
@app.websocket("/ws/alerts")
async def ws_alerts(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)

if __name__ == "__main__":
    # ensure analyzer warmed up
    try:
        get_face_analyzer()
        print("Face analyzer ready (GPU preferred).")
    except Exception as e:
        print("Face analyzer failed to init:", e)
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
