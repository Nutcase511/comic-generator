@echo off
echo 正在停止后端服务...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo 启动后端服务...
cd /d "%~dp0backend"
python main.py
pause
