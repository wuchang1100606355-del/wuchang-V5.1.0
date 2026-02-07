@echo off
setlocal
set VM_URL=http://192.168.50.249:8080

REM 啟動 POS 端代理（同步/重載 Odoo POS UI）
"%~dp0\.venv\Scripts\python.exe" "%~dp0\sister_agent.py" --device POS --vm-url %VM_URL%
endlocal
