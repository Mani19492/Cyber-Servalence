from supabase import create_client
from .config import settings

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# -------- Users -------- #

def create_user(email: str, hashed_password: str, role: str = "viewer"):
    return supabase.table("users").insert({
        "email": email,
        "hashed_password": hashed_password,
        "role": role
    }).execute().data[0]

def get_user_by_email(email: str):
    res = supabase.table("users").select("*").eq("email", email).execute()
    if res.data:
        return res.data[0]
    return None

# -------- Persons -------- #

def insert_person(name: str, metadata: dict, embedding: str):
    return supabase.table("persons").insert({
        "name": name,
        "metadata": metadata,
        "embedding": embedding
    }).execute().data[0]

def get_all_persons():
    return supabase.table("persons").select("*").execute().data

# -------- Cameras -------- #

def insert_camera(id_: str, rtsp_url: str, location: str = "", metadata: dict = None):
    return supabase.table("cameras").insert({
        "id": id_,
        "rtsp_url": rtsp_url,
        "location": location,
        "metadata": metadata or {}
    }).execute().data[0]

def get_all_cameras():
    return supabase.table("cameras").select("*").execute().data

# -------- Detections -------- #

def insert_detection(person_id, camera_id, timestamp, confidence, snapshot_path, raw_metadata=None):
    return supabase.table("detections").insert({
        "person_id": person_id,
        "camera_id": camera_id,
        "timestamp": timestamp,
        "confidence": confidence,
        "snapshot_path": snapshot_path,
        "raw_metadata": raw_metadata or {}
    }).execute().data[0]
