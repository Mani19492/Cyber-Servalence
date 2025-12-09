"""
Camera worker that reads RTSP, runs detection+embedding on GPU (via insightface),
uses DeepSort tracker, stores snapshots & detection logs to Supabase, pushes alerts via callback.
"""

import os
import time
import cv2
import asyncio
from datetime import datetime
from deep_sort_realtime.deepsort_tracker import DeepSort
from .face import detect_faces, get_embedding_from_face, load_persons_cache, match_embedding
from .mjpeg import update_frame
from .db import insert_detection
from .config import settings

ALERT_CALLBACK = None  # will be set by main.py

_trackers = {}  # camera_id -> DeepSort instance

def get_tracker(camera_id: str):
    if camera_id not in _trackers:
        # default config; adjust as needed for performance
        _trackers[camera_id] = DeepSort(max_age=30, n_init=1, max_cosine_distance=0.7)
    return _trackers[camera_id]

async def camera_loop(camera_id: str, rtsp_url: str):
    print(f"[camera_loop] starting {camera_id} -> {rtsp_url}")
    cap = cv2.VideoCapture(rtsp_url)
    persons_cache = load_persons_cache()
    last_reload = time.time()

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            # retry with small delay
            await asyncio.sleep(1.0)
            continue

        # update mjpeg view
        update_frame(camera_id, frame)

        # refresh cache periodically
        if time.time() - last_reload > 60:
            persons_cache = load_persons_cache()
            last_reload = time.time()

        # detect faces (insightface)
        try:
            dets = detect_faces(frame)
        except Exception as e:
            print("face detect error:", e)
            dets = []

        # build detections for DeepSort: [x1,y1,x2,y2,conf, class]
        ds_dets = []
        for d in dets:
            x1,y1,x2,y2 = d["bbox"]
            conf = d.get("score", 0.9)
            ds_dets.append([float(x1), float(y1), float(x2), float(y2), float(conf), 0])

        tracker = get_tracker(camera_id)
        tracks = tracker.update_tracks(ds_dets, frame=frame)

        # iterate tracks
        for t in tracks:
            if not t.is_confirmed():
                continue
            track_id = t.track_id
            l, t_y, r, b = t.to_ltrb()
            x, y, w, h = int(l), int(t_y), int(r - l), int(b - t_y)
            # crop face region (clamp)
            x2 = x + w
            y2 = y + h
            h_frame, w_frame = frame.shape[:2]
            x = max(0, x); y = max(0, y); x2 = min(w_frame-1, x2); y2 = min(h_frame-1, y2)
            if x2 - x <= 8 or y2 - y <= 8:
                continue
            face_crop = frame[y:y2, x:x2]
            try:
                emb = get_embedding_from_face(face_crop)
            except Exception as e:
                # couldn't embed; skip
                continue

            best, dist = match_embedding(emb, persons_cache)
            if best and dist <= settings.SIMILARITY_THRESHOLD:
                ts = datetime.utcnow().isoformat()
                os.makedirs("snapshots", exist_ok=True)
                fname = f"{camera_id}_{int(time.time())}_{track_id}.jpg"
                path = os.path.join("snapshots", fname)
                cv2.imwrite(path, frame)

                # write detection to DB
                try:
                    insert_detection(best["id"], camera_id, ts, float(dist), fname, {"bbox":[x,y,w,h], "track_id": track_id})
                except Exception as e:
                    print("DB insert_detection error:", e)

                # send alert
                alert = {
                    "camera_id": camera_id,
                    "timestamp": ts,
                    "person": {"id": best.get("id"), "name": best.get("name")},
                    "confidence": float(dist),
                    "snapshot": fname,
                    "track_id": track_id
                }
                if ALERT_CALLBACK:
                    try:
                        await ALERT_CALLBACK(alert)
                    except Exception as e:
                        print("alert callback failed:", e)

        await asyncio.sleep(0.01)
