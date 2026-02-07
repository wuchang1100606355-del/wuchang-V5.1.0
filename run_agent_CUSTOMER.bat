@echo off
setlocal
set VM_URL=http://192.168.50.249:8080

REM 啟動客顯端代理（同步/重載 Odoo 顧客顯示 UI）
"%~dp0\.venv\Scripts\python.exe" "%~dp0\sister_agent.py" --device CUSTOMER --vm-url %VM_URL%
endlocal
