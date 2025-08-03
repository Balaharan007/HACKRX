@echo off
title HackRx 6.0 Document Intelligence Agent

echo ████████████████████████████████████████████████████████████████
echo ██        🎯 HackRx 6.0 Document Intelligence Agent          ██
echo ████████████████████████████████████████████████████████████████
echo.

REM Check if .env file exists
if not exist ".env" (
    echo ❌ .env file not found! Please create it with your API keys.
    pause
    exit /b 1
)

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo 🔧 Activating virtual environment...
    call venv\Scripts\activate
)

echo 🚀 Choose your startup method:
echo.
echo 1. Quick Start (Recommended) - Opens separate windows
echo 2. Manual Step-by-Step
echo 3. Exit
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" goto quickstart
if "%choice%"=="2" goto manual
if "%choice%"=="3" goto end

:quickstart
echo.
echo 🌐 Starting FastAPI server in separate window...
start "HackRx FastAPI Server" cmd /k "title HackRx FastAPI Server & echo ✅ FastAPI Server Running & echo 📍 http://localhost:8000 & echo 📍 Keep this window open & echo. & python -m uvicorn main_final:app --host 0.0.0.0 --port 8000 --reload"

echo ⏳ Waiting 15 seconds for FastAPI to start...
timeout /t 15 /nobreak > nul

echo 🎨 Starting Streamlit UI in separate window...
start "HackRx Streamlit UI" cmd /k "title HackRx Streamlit UI & echo ✅ Streamlit UI Running & echo 📍 http://localhost:8501 & echo 📍 Keep this window open & echo. & streamlit run streamlit_app_v2.py --server.port 8501"

echo.
echo ✅ Both services are starting in separate windows!
echo 📍 FastAPI: http://localhost:8000
echo 📍 Streamlit: http://localhost:8501
echo.
echo 💡 If you get connection errors, wait a moment longer for services to start.
goto end

:manual
echo.
echo 📋 Manual Setup Instructions:
echo.
echo 1. Open first terminal and run: step1_fastapi.bat
echo 2. Wait for FastAPI to start (you'll see "Application startup complete")
echo 3. Open second terminal and run: step2_streamlit.bat
echo.
echo 📁 Files created for you:
echo   - step1_fastapi.bat (FastAPI server)
echo   - step2_streamlit.bat (Streamlit UI)
echo.
goto end

:end
echo.
echo 🎯 HackRx 6.0 Document Intelligence Agent setup complete!
echo.
pause
