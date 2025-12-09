# Cyber Servalence

A large-scale, real-time **face search, identification, and tracking system** designed for multi-camera cyber surveillance.

> ⚠️ For ethical & legal use only, with proper permissions and under relevant laws.

## Features

- Python **FastAPI** backend
- Face recognition with **ArcFace** (DeepFace)
- Face detection with **RetinaFace**
- Multi-camera tracking using **DeepSORT-style** tracking
- **Supabase** (PostgreSQL) as database
- **JWT auth + RBAC** (admin/operator/viewer)
- **Next.js + Tailwind** dashboard
- Live MJPEG camera streams
- Real-time WebSocket alerts with snapshots
- Dockerized backend & frontend

## Project Structure

```bash
cyber-servalence/
├── docker-compose.yml
├── README.md
├── backend/
│   ├── app/  # FastAPI, recognition, workers
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
└── frontend/
    ├── package.json
    ├── next.config.js
    ├── tailwind.config.js
    ├── pages/
    ├── components/
    └── styles/
# Cyber Servalence — GPU Setup & Run (RTX/CUDA)

You have an NVIDIA GPU (RTX 3050) with CUDA 13.0 — this guide runs the GPU-optimized backend.

## Requirements (host)
- Docker Desktop (Windows) with **WSL2 backend**
- NVIDIA drivers installed (you already have Driver 581.32)
- NVIDIA Container Toolkit (nvidia-docker) / Docker Desktop GPU support

### Install NVIDIA Container Toolkit (Windows / WSL2)
Follow NVIDIA's instructions:
https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

Make sure `docker info` shows `Runtimes: nvidia`.

## Option A — Run locally (no Docker)
You already installed Python 3.10 and GPU-capable packages. From backend folder:
1. Ensure `.env` is populated (copy `.env.example`).
2. Start FastAPI:
   ```bash
   py -3.10 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
