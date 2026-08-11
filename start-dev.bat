@echo off
REM Sobe backend (FastAPI/uvicorn) e frontend (Next.js) em janelas separadas

set ROOT=%~dp0

start "FiscalCheck - Backend" cmd /k "cd /d "%ROOT%backend" && uv run uvicorn app.main:app --reload --port 8000"
start "FiscalCheck - Frontend" cmd /k "cd /d "%ROOT%frontend" && npm run dev"

echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
