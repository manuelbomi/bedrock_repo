@echo off
echo =====================================
echo Bedrock Agent UI - Development Mode
echo =====================================
echo.

REM Check if running in the correct directory
if not exist "backend" (
    echo Error: Please run this script from the project root directory
    pause
    exit /b 1
)

echo Starting backend and frontend servers...
echo.
echo Backend will run on: http://localhost:8000
echo Frontend will run on: http://localhost:3000
echo.
echo Press Ctrl+C to stop both servers
echo.

REM Start backend in a new window
start "Bedrock Agent Backend" cmd /k "cd backend && python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000"

REM Wait a bit for backend to start
timeout /t 3 /nobreak > nul

REM Start frontend in a new window
start "Bedrock Agent Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Both servers are starting in separate windows
echo Please check the new windows for server output
echo.
pause
