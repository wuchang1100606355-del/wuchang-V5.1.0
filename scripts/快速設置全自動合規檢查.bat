@echo off
REM 快速設置全自動合規和證書檢查定時任務
REM 符合 Google 非營利組織合規要求
REM 授予工作內所必要之權限

echo ==========================================
echo   設置全自動合規和證書檢查定時任務
echo   Google 非營利組織合規確認
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
echo 合規要求: 符合 Google 非營利組織合規要求
echo 權限: 授予工作內所必要之權限
echo.

REM 檢查並安裝必要套件
echo 檢查必要套件...
python -m pip install dnspython requests urllib3 --quiet 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ 套件檢查完成
) else (
    echo ⚠ 套件安裝可能失敗，請手動檢查
)

echo.

REM 以管理員權限運行 PowerShell 腳本
powershell -ExecutionPolicy Bypass -File "setup_auto_compliance_task.ps1"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==========================================
    echo   設置完成！
    echo ==========================================
    echo.
    echo 定時任務已創建，系統將每小時自動執行：
    echo   1. 確認首頁由 wuchang.life 可連
    echo   2. Google 非營利組織合規確認 DNS 狀態
    echo   3. 自動完成憑證簽發（Caddy + Let's Encrypt）
    echo   4. 無人職守全自動執行
    echo   5. 授予工作內所必要之權限
    echo.
    echo 您可以：
    echo   1. 立即測試執行: python scripts\auto_compliance_certificate_check.py
    echo   2. 查看任務狀態: 打開「工作排程器」，搜尋「WuchangAutoComplianceCheck」
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
    echo   4. 已安裝必要套件: dnspython, requests, urllib3
    echo.
)

pause
