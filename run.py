import subprocess
import time
import os
import sys

print("=" * 50)
print("Starting CYBER SERVALENCE...")
print("=" * 50 + "\n")

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT, "backend")
FRONTEND_DIR = os.path.join(ROOT, "frontend")

# Check if .env file exists
env_file = os.path.join(ROOT, ".env")
if not os.path.exists(env_file):
    print("[!] WARNING: .env file not found at root directory!")
    print("[!] Please create .env file with required variables:")
    print("    - SUPABASE_URL")
    print("    - SUPABASE_KEY")
    print("    - FERNET_KEY")
    print("    - JWT_SECRET")
    print()
    response = input("Continue anyway? (y/n): ")
    if response.lower() != 'y':
        sys.exit(1)

# Check if frontend dependencies are installed
frontend_node_modules = os.path.join(FRONTEND_DIR, "node_modules")
if not os.path.exists(frontend_node_modules):
    print("[!] Frontend dependencies not found. Installing...")
    print(f"[+] Running: npm install in {FRONTEND_DIR}")
    subprocess.run(["npm", "install"], cwd=FRONTEND_DIR, shell=True)
    print()

# Start Backend
print("[+] Starting Backend on http://localhost:8000 ...")
try:
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        cwd=BACKEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print(f"[+] Backend process started (PID: {backend_process.pid})")
except Exception as e:
    print(f"[!] Error starting backend: {e}")
    sys.exit(1)

# Wait for backend to initialize
print("[+] Waiting for backend to initialize...")
time.sleep(5)

# Start Frontend
print("[+] Starting Frontend on http://localhost:3000 ...")
try:
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=FRONTEND_DIR,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print(f"[+] Frontend process started (PID: {frontend_process.pid})")
except Exception as e:
    print(f"[!] Error starting frontend: {e}")
    print("[!] Make sure Node.js and npm are installed")
    backend_process.terminate()
    sys.exit(1)

print("\n" + "=" * 50)
print(" CYBER SERVALENCE IS RUNNING ")
print("=" * 50)
print("Backend  → http://localhost:8000")
print("Frontend → http://localhost:3000")
print("API Docs → http://localhost:8000/docs")
print("\nPress CTRL+C to stop all servers")
print("=" * 50 + "\n")

# Keep script running and handle cleanup
try:
    # Monitor processes
    while True:
        # Check if processes are still running
        if backend_process.poll() is not None:
            print("[!] Backend process has stopped!")
            break
        if frontend_process.poll() is not None:
            print("[!] Frontend process has stopped!")
            break
        time.sleep(2)
except KeyboardInterrupt:
    print("\n[!] Shutting down servers...")
    backend_process.terminate()
    frontend_process.terminate()
    print("[+] Servers stopped")
