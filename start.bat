@echo off
REM HackRx 6.0 Document Intelligence Agent - Windows Startup Script

echo 🚀 Starting HackRx 6.0 Document Intelligence Agent...

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found! Please create it with your API keys.
    pause
    exit /b 1
)

REM Start FastAPI server in background
echo 🌐 Starting FastAPI server...
start /B python main.py

REM Wait a moment for FastAPI to start
timeout /t 5 /nobreak > nul

REM Start Streamlit app
echo 🎨 Starting Streamlit interface...
streamlit run streamlit_app.py --server.port 8501

pause
