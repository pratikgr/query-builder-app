@echo off
REM Start Backend and Frontend Development Servers for Windows

echo ===================================
echo Query Builder Application Setup
echo ===================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Node.js is not installed
    exit /b 1
)

REM Backend Setup
echo Setting up backend...
cd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing backend dependencies...
pip install -r requirements.txt

REM Create .env if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
)

REM Initialize database
echo Initializing database...
python -m app.db.init_db

echo.
echo Starting FastAPI backend on http://localhost:8000
start cmd /k "venv\Scripts\activate.bat && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

cd ..

REM Frontend Setup
echo.
echo Setting up frontend...
cd frontend

if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)

REM Create .env if it doesn't exist
if not exist ".env" (
    echo Creating frontend .env file...
    copy .env.example .env
)

echo.
echo Starting React frontend on http://localhost:3000
start cmd /k "npm start"

cd ..

echo.
echo ===================================
echo Application started successfully!
echo ===================================
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend: http://localhost:3000
echo.
echo Close the command windows to stop the servers
echo ===================================

pause
