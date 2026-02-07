@echo off
REM 啟動地端小 j 與 JULES 容器維護協作（每小時檢查一次）
cd /d "C:\wuchang V5.1.0\wuchang-V5.1.0"
start "地端小j-容器協作" /min python little_j_jules_container_collaboration.py --interval 3600
echo 地端小 j 容器維護協作已啟動（每小時檢查一次）
echo 查看日誌: type container_collaboration.log
pause
