@echo off
TITLE Vengeance Bot Installer
COLOR 0A

echo ╔══════════════════════════════════════════════════════════════╗
echo ║     🦅 VENGEANCE BOT - Cybersecurity Command Center        ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check Python
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.9+ from python.org
    pause
    exit /b 1
)
python --version
echo ✅ Python found

REM Create virtual environment
echo.
echo [2/6] Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment created

REM Activate virtual environment
echo.
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat
echo ✅ Virtual environment activated

REM Upgrade pip
echo.
echo [4/6] Upgrading pip...
python -m pip install --upgrade pip
echo ✅ pip upgraded

REM Install requirements
echo.
echo [5/6] Installing dependencies (this may take a few minutes)...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed

REM Create directories
echo.
echo [6/6] Creating directories...
mkdir .vengeance 2>nul
mkdir reports 2>nul
mkdir logs 2>nul
mkdir data 2>nul
mkdir .vengeance\phishing 2>nul
mkdir .vengeance\captured 2>nul
mkdir .vengeance\wordlists 2>nul
mkdir .vengeance\ssh_keys 2>nul
mkdir .vengeance\traffic_logs 2>nul
mkdir .vengeance\nikto_results 2>nul
echo ✅ Directories created

REM Create .env file
if not exist .env (
    copy .env.example .env
    echo ⚠️ Created .env file - please edit with your configuration
)

REM Final message
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║              ✅ INSTALLATION COMPLETE!                        ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo To start Vengeance Bot:
echo   venv\Scripts\activate
echo   python vengeance.py
echo.
echo To run health check:
echo   python healthcheck.py
echo.
echo Web Dashboard:
echo   http://localhost:5000
echo.
pause