import cv2
import threading
import numpy as np
import os
from datetime import datetime
from .face import detect_faces
from .db import get_all_persons, insert_detection
from .mjpeg import update_frame
from .config import settings

def cosine_distance(emb1, emb2):
    """Calculate cosine distance between two embeddings"""
    emb1 = np.array(emb1)
    emb2 = np.array(emb2)
    dot_product = np.dot(emb1, emb2)
    norm1 = np.linalg.norm(emb1)
    norm2 = np.linalg.norm(emb2)
    if norm1 == 0 or norm2 == 0:
        return 1.0
    cosine_sim = dot_product / (norm1 * norm2)
    return 1.0 - cosine_sim

def save_snapshot(frame, camera_id, person_name):
    """Save detection snapshot"""
    os.makedirs("snapshots", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{camera_id}_{person_name}_{timestamp}.jpg"
    filepath = os.path.join("snapshots", filename)
    cv2.imwrite(filepath, frame)
    return filename

class CameraWorker(threading.Thread):
    def __init__(self, cam_id: str, url: str, alert_callback=None):
        super().__init__(daemon=True)
        self.cam_id = cam_id
        self.url = url
        self.running = True
        self.alert_callback = alert_callback
        self.frame_count = 0

    def run(self):
        cap = cv2.VideoCapture(self.url)
        if not cap.isOpened():
            print(f"Failed to open camera {self.cam_id}: {self.url}")
            return

        while self.running:
            ret, frame = cap.read()
            if not ret:
                import time
                time.sleep(1)
                continue

            self.frame_count += 1
            # Update MJPEG stream
            update_frame(self.cam_id, frame)

            # Process every 10th frame for performance
            if self.frame_count % 10 != 0:
                continue

            try:
                faces = detect_faces(frame)
                persons = get_all_persons()

                for f in faces:
                    emb = f.embedding.tolist()
                    # Get bounding box if available
                    bbox = None
                    if hasattr(f, 'bbox') and f.bbox is not None:
                        bbox = f.bbox.astype(int)
                    elif hasattr(f, 'det_bbox'):
                        bbox = f.det_bbox.astype(int)

                    # Draw bounding box on frame if available
                    if bbox is not None and len(bbox) >= 4:
                        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)

                    # Compare with database
                    best_match = None
                    best_dist = 1.0

                    for p in persons:
                        db_emb = p["embedding"]
                        dist = cosine_distance(db_emb, emb)

                        if dist < best_dist and dist < settings.similarity_threshold:
                            best_dist = dist
                            best_match = p

                    if best_match:
                        # Save snapshot
                        snapshot_file = save_snapshot(frame, self.cam_id, best_match["name"])
                        
                        # Insert detection
                        insert_detection(
                            best_match["id"], 
                            self.cam_id,
                            float(best_dist),
                            snapshot_file
                        )

                        # Send alert via callback
                        if self.alert_callback:
                            alert_data = {
                                "camera_id": self.cam_id,
                                "timestamp": datetime.now().isoformat(),
                                "person": {"name": best_match["name"], "id": best_match["id"]},
                                "confidence": float(best_dist),
                                "snapshot": snapshot_file,
                                "track_id": None
                            }
                            # Run async callback in event loop
                            import asyncio
                            try:
                                loop = asyncio.get_event_loop()
                                if loop.is_running():
                                    asyncio.create_task(self.alert_callback(alert_data))
                                else:
                                    loop.run_until_complete(self.alert_callback(alert_data))
                            except RuntimeError:
                                # No event loop running, create new one
                                try:
                                    asyncio.run(self.alert_callback(alert_data))
                                except:
                                    pass
                            except:
                                # Fallback if event loop issues
                                pass

                        # Draw name on frame if bbox is available
                        if bbox is not None and len(bbox) >= 4:
                            cv2.putText(
                                frame, 
                                best_match["name"], 
                                (bbox[0], max(bbox[1] - 10, 20)),
                                cv2.FONT_HERSHEY_SIMPLEX, 
                                0.7, 
                                (0, 255, 0), 
                                2
                            )

                # Update frame with annotations
                update_frame(self.cam_id, frame)

            except Exception as e:
                print(f"Error processing frame for {self.cam_id}: {e}")

        cap.release()
