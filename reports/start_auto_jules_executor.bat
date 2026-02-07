@echo off
REM ============================================
REM 啟動 JULES 任務自動執行器（背景運行）
REM ============================================

cd /d "%~dp0"

echo 正在啟動 JULES 任務自動執行器...
echo 檢查間隔: 60 秒
echo.
echo 此視窗可以關閉，執行器將在背景運行
echo 日誌檔案: jules_task_executor.log
echo.

start "JULES 任務自動執行器" /min python auto_jules_task_executor.py --interval 60

timeout /t 3 /nobreak >nul

echo ✓ 執行器已啟動（背景運行）
echo.
echo 查看日誌: type jules_task_executor.log
echo 停止執行器: 在任務管理器中結束 Python 進程
echo.

pause
