@echo off
REM 快速設置優化架構
REM 利用 Windows 10 專業版功能
REM 合規要求：符合 Google 非營利組織合規要求

echo ==========================================
echo   Wuchang 系統優化架構設置
echo   利用 Windows 10 專業版功能
echo ==========================================
echo.

cd /d "%~dp0.."

REM 檢查管理員權限
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 錯誤: 需要管理員權限
    echo 請以管理員權限運行此腳本
    pause
    exit /b 1
)

echo 正在設置優化架構...
echo.

REM 執行 PowerShell 設置腳本
powershell -ExecutionPolicy Bypass -File "scripts\setup_optimized_architecture.ps1"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==========================================
    echo   設置完成！
    echo ==========================================
    echo.
    echo 優化架構已設置完成，系統現在具有：
    echo   - 統一任務管理系統
    echo   - 系統服務自動監控和恢復
    echo   - 容器健康監控和自動恢復
    echo   - 優化的資源管理
    echo   - 增強的健康檢查
    echo.
) else (
    echo.
    echo ==========================================
    echo   設置失敗
    echo ==========================================
    echo.
    echo 請檢查錯誤信息並重試
    echo.
)

pause
