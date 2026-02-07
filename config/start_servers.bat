@echo off
REM ============================================
REM 五常系統 - 伺服器開機自動部署腳本
REM ============================================
REM 此腳本用於在 Windows 開機時自動啟動所有服務器
REM
REM 使用方式：
REM   1. 直接執行：雙擊此檔案
REM   2. 開機自動執行：使用 setup_auto_start.ps1 註冊到任務計劃程序
REM ============================================

setlocal enabledelayedexpansion

REM 設定工作目錄為腳本所在目錄
cd /d "%~dp0"

REM 設定 Python 路徑（如果不在 PATH 中，請修改此處）
set PYTHON_CMD=python

REM 設定日誌目錄
set LOG_DIR=logs
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM 設定日誌檔案（使用日期時間戳）
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do set DATE_STR=%%c-%%a-%%b
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set TIME_STR=%%a%%b
set TIME_STR=!TIME_STR: =0!
set LOG_FILE=%LOG_DIR%\server_startup_%DATE_STR%_%TIME_STR%.log

REM 開始記錄
echo ============================================ >> "%LOG_FILE%"
echo 伺服器啟動日誌 - %date% %time% >> "%LOG_FILE%"
echo ============================================ >> "%LOG_FILE%"
echo.

REM 檢查 Python 是否可用
%PYTHON_CMD% --version >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo [錯誤] Python 未安裝或不在 PATH 中 >> "%LOG_FILE%"
    echo [錯誤] 請確認 Python 已正確安裝並添加到系統 PATH
    pause
    exit /b 1
)

REM 檢查必要檔案是否存在
if not exist "local_control_center.py" (
    echo [錯誤] 找不到 local_control_center.py >> "%LOG_FILE%"
    echo [錯誤] 請確認腳本位於正確的目錄
    pause
    exit /b 1
)

if not exist "little_j_hub_server.py" (
    echo [警告] 找不到 little_j_hub_server.py，將跳過此服務 >> "%LOG_FILE%"
)

REM 啟動服務器（在背景執行）
echo [%date% %time%] 開始啟動服務器... >> "%LOG_FILE%"
echo.

REM 1. 啟動本機中控台 (local_control_center.py)
echo [%date% %time%] 啟動本機中控台 (端口 8788)... >> "%LOG_FILE%"
start "五常-本機中控台" /min %PYTHON_CMD% local_control_center.py --port 8788 >> "%LOG_DIR%\control_center.log" 2>&1
timeout /t 2 /nobreak >nul

REM 2. 啟動 Little J Hub 服務器 (little_j_hub_server.py)
REM 注意：需要設定環境變數 WUCHANG_HUB_TOKEN
if exist "little_j_hub_server.py" (
    echo [%date% %time%] 啟動 Little J Hub 服務器 (端口 8799)... >> "%LOG_FILE%"
    if defined WUCHANG_HUB_TOKEN (
        start "五常-LittleJ-Hub" /min %PYTHON_CMD% little_j_hub_server.py --bind 127.0.0.1 --port 8799 --root ./little_j_hub >> "%LOG_DIR%\little_j_hub.log" 2>&1
        echo [%date% %time%] Little J Hub 服務器已啟動 >> "%LOG_FILE%"
    ) else (
        echo [警告] WUCHANG_HUB_TOKEN 未設定，跳過 Little J Hub 服務器 >> "%LOG_FILE%"
        echo [提示] 如需啟動此服務，請設定環境變數 WUCHANG_HUB_TOKEN >> "%LOG_FILE%"
    )
    timeout /t 2 /nobreak >nul
)

REM 等待服務啟動
echo [%date% %time%] 等待服務初始化... >> "%LOG_FILE%"
timeout /t 5 /nobreak >nul

REM 檢查服務是否正常運行
echo [%date% %time%] 檢查服務狀態... >> "%LOG_FILE%"

REM 檢查端口 8788 (本機中控台)
netstat -an | findstr ":8788" >nul
if errorlevel 1 (
    echo [警告] 本機中控台可能未正常啟動 (端口 8788) >> "%LOG_FILE%"
) else (
    echo [成功] 本機中控台運行中 (http://127.0.0.1:8788/) >> "%LOG_FILE%"
)

REM 檢查端口 8799 (Little J Hub)
netstat -an | findstr ":8799" >nul
if errorlevel 1 (
    echo [警告] Little J Hub 可能未正常啟動 (端口 8799) >> "%LOG_FILE%"
) else (
    echo [成功] Little J Hub 運行中 (http://127.0.0.1:8799/) >> "%LOG_FILE%"
)

echo.
echo ============================================ >> "%LOG_FILE%"
echo 啟動程序完成 >> "%LOG_FILE%"
echo ============================================ >> "%LOG_FILE%"
echo.

REM 顯示啟動資訊
echo ============================================
echo 五常系統服務器已啟動
echo ============================================
echo.
echo 本機中控台: http://127.0.0.1:8788/
echo Little J Hub: http://127.0.0.1:8799/
echo.
echo 日誌檔案位置: %LOG_FILE%
echo.
echo 提示：此視窗可以關閉，服務將在背景運行
echo ============================================

REM 保持視窗開啟 5 秒後自動關閉（開機時）
REM 如果手動執行，可以註解掉下面這行以保持視窗開啟
timeout /t 5 /nobreak >nul

endlocal
