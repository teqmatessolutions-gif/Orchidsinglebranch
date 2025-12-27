Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "uvicorn" -Force -ErrorAction SilentlyContinue
Write-Host "All Python processes terminated."
Start-Sleep -Seconds 2
