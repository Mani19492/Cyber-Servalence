from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, List

# -------- Auth -------- #

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "viewer"   # admin | operator | viewer

class UserOut(BaseModel):
    id: str
    email: EmailStr
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# -------- Persons & Cameras -------- #

class PersonCreate(BaseModel):
    name: str
    metadata: Optional[Dict] = {}

class CameraCreate(BaseModel):
    id: str
    rtsp_url: str
    location: Optional[str] = ""
    metadata: Optional[Dict] = {}

# -------- Alerts (for WS/front) -------- #

class DetectionAlert(BaseModel):
    camera_id: str
    timestamp: str
    person: Dict
    confidence: float
    snapshot: str
