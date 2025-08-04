@echo off
REM Image Recognition App Startup Script for Windows

echo 🚀 Starting Image Recognition App...

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo 📥 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create uploads directory if it doesn't exist
if not exist "uploads" mkdir uploads

REM Run tests if requested
if "%1"=="--test" (
    echo 🧪 Running tests...
    pytest tests\ -v
)

REM Start the application
echo 🌟 Starting Flask application...
echo 📱 Open your browser and navigate to: http://localhost:5000
echo ⏹️  Press Ctrl+C to stop the server
echo.

python app.py

pause