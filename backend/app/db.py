from supabase import create_client
from .config import settings

supabase = create_client(settings.supabase_url, settings.supabase_key)

# ---------------------- USERS TABLE ----------------------

def get_user_by_email(email: str):
    r = supabase.table("users").select("*").eq("email", email).execute()
    if r.data:
        return r.data[0]
    return None

def create_user(email: str, password: str):
    supabase.table("users").insert({
        "email": email,
        "hashed_password": password  # Database uses hashed_password
    }).execute()

# ---------------------- PERSONS TABLE ----------------------

def insert_person(name: str, embedding: list):
    # Convert embedding list to JSON string for text storage
    import json
    embedding_json = json.dumps(embedding)
    return supabase.table("persons").insert({
        "name": name,
        "embedding": embedding_json
    }).execute()

def get_all_persons():
    r = supabase.table("persons").select("*").execute()
    # Parse embedding from JSON string back to list
    import json
    if r.data:
        for person in r.data:
            if person.get("embedding") and isinstance(person["embedding"], str):
                try:
                    person["embedding"] = json.loads(person["embedding"])
                except:
                    person["embedding"] = []
    return r.data

# ---------------------- CAMERAS TABLE ----------------------

def insert_camera(name: str, url: str, camera_id: str = None):
    # Database uses id as TEXT primary key and rtsp_url instead of url
    camera_id = camera_id or name.lower().replace(" ", "_")
    supabase.table("cameras").insert({
        "id": camera_id,
        "rtsp_url": url,
        "location": name
    }).execute()

def get_all_cameras():
    r = supabase.table("cameras").select("*").execute()
    # Map database fields to frontend expected fields
    if r.data:
        for camera in r.data:
            # Map rtsp_url to url for frontend compatibility
            if "rtsp_url" in camera:
                camera["url"] = camera["rtsp_url"]
            # Map location to name if name is not set
            if "location" in camera and camera["location"]:
                if "name" not in camera or not camera["name"]:
                    camera["name"] = camera["location"]
    return r.data

# ---------------------- DETECTIONS TABLE ----------------------

def insert_detection(person_id, camera_id, confidence, snapshot_url):
    # Database uses snapshot_path instead of snapshot_url
    from datetime import datetime
    supabase.table("detections").insert({
        "person_id": person_id,
        "camera_id": camera_id,
        "confidence": float(confidence),
        "snapshot_path": snapshot_url,
        "timestamp": datetime.utcnow().isoformat()
    }).execute()
