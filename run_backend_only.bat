@echo off
echo ========================================
echo Starting Backend Server (Skip Deps)
echo ========================================
echo.

echo Activating virtual environment...
call ResortApp\venv\Scripts\activate.bat

echo.
echo ========================================
echo Starting FastAPI Backend Server
echo ========================================
echo Backend will be available at: http://localhost:8011
echo API Documentation: http://localhost:8011/docs
echo.
echo Press Ctrl+C to stop the server
echo.

cd ResortApp
python main.py
cd ..

pause
