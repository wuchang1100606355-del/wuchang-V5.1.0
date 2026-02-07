@echo off
REM 每小時檢查系統部署狀態的批處理腳本
REM 此腳本可以由 Windows 定時任務調用

setlocal

set PROJECT_ROOT=%~dp0..
set PYTHON_SCRIPT=%PROJECT_ROOT%\scripts\comprehensive_hourly_check.py
set LOG_DIR=%PROJECT_ROOT%\logs
set LOG_FILE=%LOG_DIR%\hourly_check_%DATE:~0,4%%DATE:~5,2%%DATE:~8,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%.log

REM 創建日誌目錄
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM 記錄開始時間
echo [%DATE% %TIME%] 開始執行每小時檢查 >> "%LOG_FILE%"
echo ========================================== >> "%LOG_FILE%"

REM 執行 Python 腳本
python "%PYTHON_SCRIPT%" >> "%LOG_FILE%" 2>&1
set EXIT_CODE=%ERRORLEVEL%

REM 記錄結束時間和退出碼
echo ========================================== >> "%LOG_FILE%"
echo [%DATE% %TIME%] 執行完成，退出碼: %EXIT_CODE% >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

REM 如果有錯誤，發送通知（可選）
if %EXIT_CODE% NEQ 0 (
    echo 檢查發現問題，退出碼: %EXIT_CODE% >> "%LOG_FILE%"
)

exit /b %EXIT_CODE%
