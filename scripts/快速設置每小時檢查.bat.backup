@echo off
REM 快速設置每小時檢查系統部署狀態的批處理腳本
REM 此腳本會自動設置 Windows 定時任務

echo ==========================================
echo   設置每小時系統部署檢查定時任務
echo ==========================================
echo.

cd /d "%~dp0"

REM 檢查 PowerShell 是否可用
powershell -Command "Write-Host '檢查 PowerShell 環境...'" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 錯誤: PowerShell 不可用
    pause
    exit /b 1
)

echo 正在設置定時任務...
echo.

REM 以管理員權限運行 PowerShell 腳本
powershell -ExecutionPolicy Bypass -File "setup_hourly_check_task.ps1"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==========================================
    echo   設置完成！
    echo ==========================================
    echo.
    echo 定時任務已創建，系統將每小時自動檢查一次。
    echo.
    echo 您可以：
    echo   1. 立即測試執行: python hourly_deployment_check.py
    echo   2. 查看任務狀態: 打開「工作排程器」，搜尋「WuchangHourlyDeploymentCheck」
    echo.
) else (
    echo.
    echo ==========================================
    echo   設置失敗
    echo ==========================================
    echo.
    echo 請確認：
    echo   1. 以管理員權限運行此腳本
    echo   2. Python 已正確安裝並在 PATH 中
    echo   3. 腳本文件存在於當前目錄
    echo.
)

pause
