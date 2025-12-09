"""
GPU-optimized face module using insightface + onnxruntime-gpu.
Provides:
- FaceAnalysis init that prefers CUDA provider
- detect_faces(frame) -> list of dicts {bbox, score, embedding}
- get_embedding(face_img) -> np.ndarray
- match against persons cache
"""

import os
import numpy as np
import cv2
from typing import List, Tuple, Dict, Optional
from insightface.app import FaceAnalysis
from insightface.data import get_image as _gi  # not used but insightface requires import
from .utils import decrypt_embedding, cosine_distance
from .db import get_all_persons
from .config import settings

# Configure FaceAnalysis to use onnxruntime GPU provider if possible.
# InsightFace's FaceAnalysis will use onnxruntime; we instruct it to use CUDA EP.
_face_analyzer: Optional[FaceAnalysis] = None

def get_face_analyzer():
    global _face_analyzer
    if _face_analyzer is not None:
        return _face_analyzer

    providers = []
    try:
        # prefer CUDAExecutionProvider, fall back to CPU if not available
        import onnxruntime as ort
        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
    except Exception:
        providers = ["CPUExecutionProvider"]

    # model_name 'buffalo_sc' uses SCRFD detector + ArcFace embedding (good combo)
    _face_analyzer = FaceAnalysis(allowed_modules=['detection', 'recognition'],
                                  providers=providers,
                                  det_size=(640,640))
    _face_analyzer.prepare(ctx_id=0, det_size=(640,640))  # ctx_id=0 selects GPU when available
    return _face_analyzer

def detect_faces(frame: np.ndarray) -> List[Dict]:
    """
    Detect faces and return list of dicts:
    { 'bbox': [x1,y1,x2,y2], 'score': float, 'embedding': np.ndarray (float32), 'det': detection_obj }
    """
    fa = get_face_analyzer()
    # insightface expects BGR or RGB? FaceAnalysis accepts BGR numpy (OpenCV)
    results = fa.get(frame)
    out = []
    for r in results:
        # r.bbox is [x1, y1, x2, y2]
        emb = r.normed_embedding.astype('float32') if hasattr(r, 'normed_embedding') else None
        out.append({
            "bbox": [int(r.bbox[0]), int(r.bbox[1]), int(r.bbox[2]), int(r.bbox[3])],
            "score": float(r.det_score if hasattr(r,'det_score') else r.score if hasattr(r,'score') else 0.0),
            "embedding": emb,
            "det_raw": r
        })
    return out

def get_embedding_from_face(face_img: np.ndarray) -> np.ndarray:
    """
    Accepts a cropped BGR face image, returns embedding float32.
    """
    fa = get_face_analyzer()
    # feed single image to FaceAnalysis recognition
    faces = fa.get(face_img)
    if not faces:
        # fallback: resize and run again
        face_small = cv2.resize(face_img, (160,160))
        faces = fa.get(face_small)
        if not faces:
            raise ValueError("Could not extract embedding")
    emb = faces[0].normed_embedding.astype('float32')
    return emb

def load_persons_cache():
    return get_all_persons()

def match_embedding(vec: np.ndarray, persons_cache: List[dict]) -> Tuple[Optional[dict], float]:
    best = None
    best_d = 1.0
    if vec is None:
        return None, best_d
    for p in persons_cache:
        enc = p.get("embedding")
        if not enc:
            continue
        try:
            db_vec = decrypt_embedding(enc)
            d = cosine_distance(vec, db_vec)
            if d < best_d:
                best_d = d
                best = p
        except Exception:
            continue
    return best, best_d
