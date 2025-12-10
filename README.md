# Cyber Servalence

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

**A production-ready, real-time face recognition and multi-camera surveillance system**

*Advanced AI-powered monitoring with ArcFace recognition, DeepSORT tracking, and real-time WebSocket alerts*

</div>

---

## Overview

Cyber Servalence is an enterprise-grade surveillance platform designed for large-scale, real-time face detection, identification, and tracking across multiple camera feeds. Built with modern web technologies and AI-powered recognition models, this system provides a comprehensive solution for security monitoring and access control.

### Key Features

- **Real-Time Face Recognition** - ArcFace-based facial recognition with RetinaFace detection
- **Multi-Camera Tracking** - DeepSORT-style object tracking across camera feeds
- **Live Streaming** - MJPEG camera streams with minimal latency
- **Instant Alerts** - WebSocket-based real-time detection notifications
- **Role-Based Access Control** - JWT authentication with admin/operator/viewer roles
- **Modern Dashboard** - Beautiful React interface with Tailwind CSS
- **Scalable Architecture** - FastAPI backend with Supabase PostgreSQL database
- **GPU Acceleration** - CUDA-enabled processing for high-performance inference
- **Docker Support** - Fully containerized deployment

---

## Technology Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for blazing-fast development
- **Tailwind CSS** for modern, responsive design
- **Lucide React** for crisp, scalable icons
- **WebSocket API** for real-time alerts

### Backend
- **FastAPI** - High-performance Python web framework
- **DeepFace** - Face recognition with ArcFace model
- **RetinaFace** - State-of-the-art face detection
- **DeepSORT** - Multi-object tracking algorithm
- **PostgreSQL** (via Supabase) - Robust relational database
- **JWT** - Secure token-based authentication

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **NVIDIA CUDA** - GPU acceleration support
- **WSL2** - Windows subsystem for Linux

---

## Project Structure

```
cyber-servalence/
├── frontend/                    # React + Vite frontend
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   │   ├── CameraGrid.tsx  # Live camera feed grid
│   │   │   └── AlertsPanel.tsx # Real-time alerts panel
│   │   ├── App.tsx             # Main application component
│   │   ├── main.tsx            # React entry point
│   │   └── index.css           # Global styles + animations
│   ├── package.json            # Frontend dependencies
│   ├── vite.config.ts          # Vite configuration
│   └── tailwind.config.js      # Tailwind CSS config
│
├── backend/                     # FastAPI backend
│   ├── app/
│   │   ├── main.py             # FastAPI application
│   │   ├── auth.py             # JWT authentication
│   │   ├── recognition.py      # Face recognition engine
│   │   ├── tracking.py         # DeepSORT tracker
│   │   ├── database.py         # Database models & queries
│   │   └── workers.py          # Background workers
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile              # Backend container
│   └── .env.example            # Environment variables template
│
├── docker-compose.yml          # Multi-container orchestration
└── README.md                   # This file
```

---

## Getting Started

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.10+
- **Docker Desktop** (for containerized deployment)
- **NVIDIA GPU** (optional, for GPU acceleration)
- **CUDA 11.0+** (if using GPU)

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/cyber-servalence.git
   cd cyber-servalence
   ```

2. **Backend configuration**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your configuration:
   # - SUPABASE_URL
   # - SUPABASE_KEY
   # - JWT_SECRET
   # - DATABASE_URL
   ```

3. **Frontend configuration**
   ```bash
   cd frontend
   cp .env.example .env
   # Add your backend URL:
   # VITE_BACKEND_URL=http://localhost:8000
   ```

### Installation & Running

#### Option A: Docker Deployment (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

#### Option B: Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## Configuration

### Database Setup (Supabase)

1. Create a Supabase project at https://supabase.com
2. Create the following tables in your PostgreSQL database:

```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'viewer',
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Cameras table
CREATE TABLE cameras (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  location TEXT,
  rtsp_url TEXT,
  status TEXT DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Persons table (known individuals)
CREATE TABLE persons (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  embedding VECTOR(512),
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Detections table
CREATE TABLE detections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  camera_id UUID REFERENCES cameras(id),
  person_id UUID REFERENCES persons(id),
  confidence FLOAT,
  track_id TEXT,
  snapshot_url TEXT,
  timestamp TIMESTAMPTZ DEFAULT now()
);
```

3. Enable Row Level Security (RLS) policies as needed

### Environment Variables

**Backend (.env)**
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
JWT_SECRET=your_jwt_secret_key
DATABASE_URL=postgresql://user:pass@host:5432/db
CUDA_VISIBLE_DEVICES=0  # GPU device ID
```

**Frontend (.env)**
```env
VITE_BACKEND_URL=http://localhost:8000
```

---

## Usage

### Default Credentials

For initial setup, use these default credentials:
- **Email:** admin@cyber.com
- **Password:** admin123

**Important:** Change these credentials immediately after first login!

### Adding Cameras

Use the API to register new cameras:

```bash
curl -X POST http://localhost:8000/api/cameras \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Front Door",
    "location": "Main Entrance",
    "rtsp_url": "rtsp://camera-ip:554/stream"
  }'
```

### Registering Known Faces

Add individuals to the recognition database:

```bash
curl -X POST http://localhost:8000/api/persons \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "name=John Doe" \
  -F "image=@photo.jpg"
```

### Monitoring Alerts

Real-time alerts are pushed via WebSocket to the dashboard automatically. You can also query historical detections:

```bash
curl http://localhost:8000/api/detections?limit=50 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## GPU Acceleration

### NVIDIA GPU Setup (Windows with WSL2)

1. **Install NVIDIA Container Toolkit**
   ```bash
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
     sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   sudo apt-get update && sudo apt-get install -y nvidia-docker2
   sudo systemctl restart docker
   ```

2. **Verify GPU access**
   ```bash
   docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
   ```

3. **Run with GPU support**
   ```bash
   docker-compose -f docker-compose.gpu.yml up -d
   ```

---

## API Documentation

Once the backend is running, interactive API documentation is available at:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/login` | Authenticate and receive JWT token |
| GET | `/api/cameras` | List all cameras |
| POST | `/api/cameras` | Register new camera |
| GET | `/stream/{camera_id}` | MJPEG camera stream |
| GET | `/api/detections` | Query detection history |
| POST | `/api/persons` | Register known person |
| WS | `/ws/alerts` | WebSocket for real-time alerts |

---

## Security Considerations

**This system is designed for authorized use only. Please ensure:**

- All deployments comply with local privacy and surveillance laws
- Proper consent is obtained for facial recognition
- Access is restricted to authorized personnel
- Secure passwords and JWT secrets are used
- Regular security audits are performed
- Data retention policies are implemented
- HTTPS is enabled in production

---

## Performance Optimization

### Recommended Hardware

- **CPU:** 8+ cores (Intel i7/Ryzen 7 or better)
- **RAM:** 16GB minimum, 32GB recommended
- **GPU:** NVIDIA RTX 3050 or better (4GB+ VRAM)
- **Storage:** SSD with 100GB+ free space

### Tuning Tips

1. **Reduce face detection frequency** - Process every Nth frame
2. **Lower stream resolution** - Use 720p instead of 1080p
3. **Batch processing** - Group inference operations
4. **Database indexing** - Add indexes on frequently queried columns
5. **Redis caching** - Cache embeddings and frequent queries

---

## Troubleshooting

### Common Issues

**WebSocket connection fails**
```
Error: Connection error. Please check if backend is running.
```
- Verify backend is running on correct port
- Check CORS settings in FastAPI
- Ensure WebSocket URL uses `ws://` or `wss://` protocol

**Camera stream not displaying**
```
Waiting for feed...
```
- Verify RTSP URL is accessible
- Check camera credentials
- Ensure ffmpeg is installed for stream processing

**GPU not detected**
```
CUDA not available, falling back to CPU
```
- Install NVIDIA drivers
- Install CUDA toolkit
- Install GPU-enabled PyTorch: `pip install torch --index-url https://download.pytorch.org/whl/cu118`

---

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Backend linting
cd backend
black . && flake8

# Frontend linting
cd frontend
npm run lint
```

### Building for Production

```bash
# Frontend production build
cd frontend
npm run build

# Docker production image
docker build -t cyber-servalence:latest .
```

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Acknowledgments

- **DeepFace** - Face recognition framework
- **RetinaFace** - Face detection model
- **FastAPI** - Modern Python web framework
- **Supabase** - Open source Firebase alternative
- **Tailwind CSS** - Utility-first CSS framework

---

## Support

For issues, questions, or contributions:

- **GitHub Issues:** https://github.com/yourusername/cyber-servalence/issues
- **Documentation:** https://docs.cyberservalence.com
- **Email:** support@cyberservalence.com

---

<div align="center">

**Built with security and privacy in mind**

*Use responsibly and in compliance with local regulations*

</div>
