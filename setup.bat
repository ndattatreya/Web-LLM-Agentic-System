@echo off
REM Setup script for Web-LLM Agentic System Frontend on Windows

echo.
echo 🚀 Web-LLM Agentic System - Setup Script
echo ========================================
echo.

REM Setup Backend
echo Setting up Backend...
cd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -r requirements_full.txt

cd ..

REM Setup Frontend
echo Setting up Frontend...
cd frontend

echo Installing Node dependencies...
call npm install

cd ..

echo.
echo ✓ Setup complete!
echo.
echo To start the application:
echo.
echo Terminal 1 - Backend:
echo   cd backend
echo   venv\Scripts\activate.bat
echo   python app/main.py
echo.
echo Terminal 2 - Frontend:
echo   cd frontend
echo   npm run dev
echo.
echo The application will be available at http://localhost:5173
echo API documentation at http://localhost:8000/docs
echo.

pause
