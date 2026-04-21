@echo off
REM Quick setup script for Patent Intelligence Dashboard (Windows)

echo.
echo 🚀 Patent Intelligence Dashboard - Setup
echo ==========================================
echo.

REM Check Python version
python --version
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    exit /b 1
)

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ Failed to activate virtual environment
    exit /b 1
)

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📥 Installing dependencies from requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    exit /b 1
)

echo.
echo ✓ Setup complete!
echo.
echo Next steps:
echo 1. Run the pipeline: python patent_pipeline.py
echo 2. Generate visualizations: python create_visualizations.py
echo 3. Launch the dashboard: streamlit run app.py
echo.
echo 🌐 The dashboard will open at http://localhost:8501
echo.
pause
