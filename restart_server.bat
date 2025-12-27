@echo off
echo Stopping all Python processes...
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM node.exe /T 2>nul
timeout /t 2 /nobreak >nul

echo Starting server...
cd /d "%~dp0"
start "" cmd /c "run_all.bat"

echo Server restart initiated!
echo Please wait 10 seconds for the server to start...
timeout /t 10 /nobreak

echo Done! Server should be running now.
pause
