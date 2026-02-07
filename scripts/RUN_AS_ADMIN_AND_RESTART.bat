@echo off
REM 以管理員身份執行自動設定並重啟腳本

echo ========================================
echo 外接硬碟虛擬記憶體自動設定
echo ========================================
echo.
echo 此腳本將：
echo   1. 在 E: 磁碟設定虛擬記憶體（16-32 GB）
echo   2. 重新啟動電腦
echo.
echo 注意：需要管理員權限
echo.

REM 檢查管理員權限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo 正在請求管理員權限...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo 正在執行設定腳本...
echo.

REM 切換到腳本目錄
cd /d "%~dp0\.."

REM 執行 PowerShell 腳本
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\auto_setup_and_restart.ps1"

pause
