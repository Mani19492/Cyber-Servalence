echo Starting CYBER SERVALENCE...

start cmd /k "cd backend && py -3.10 -m uvicorn app.main:app --reload --port 8000"
timeout /t 3

start cmd /k "cd frontend && npm run dev"

echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
