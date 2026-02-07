@echo off
REM ============================================
REM 完整卸載全部 Docker 容器（批次檔）
REM ============================================

cd /d "%~dp0"

echo ============================================
echo 完整卸載全部 Docker 容器
echo ============================================
echo.

REM 檢查 Docker 是否可用
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未安裝或無法使用
    echo 請先安裝 Docker Desktop
    pause
    exit /b 1
)

echo ✓ Docker 已安裝
echo.

REM 檢查容器數量
echo 正在檢查容器狀態...
docker ps -a --format "{{.Names}}" >nul 2>&1
if errorlevel 1 (
    echo ❌ 無法查詢容器列表
    pause
    exit /b 1
)

echo.
echo ⚠ 警告：此操作將刪除所有容器！
echo.
set /p confirm="確認要刪除所有容器嗎？(輸入 YES 確認): "

if /i not "%confirm%"=="YES" (
    echo 操作已取消
    pause
    exit /b 0
)

echo.
echo ============================================
echo 開始卸載容器
echo ============================================
echo.

REM 停止所有容器
echo [1/3] 正在停止所有容器...
docker stop $(docker ps -q) 2>nul
if errorlevel 1 (
    echo ⚠ 部分容器停止失敗（可能已停止）
) else (
    echo ✓ 已停止所有容器
)
echo.

REM 刪除所有容器
echo [2/3] 正在刪除所有容器...
docker rm $(docker ps -a -q) 2>nul
if errorlevel 1 (
    echo ⚠ 部分容器刪除失敗，嘗試強制刪除...
    docker rm -f $(docker ps -a -q) 2>nul
    if errorlevel 1 (
        echo ❌ 刪除容器時發生錯誤
    ) else (
        echo ✓ 已強制刪除所有容器
    )
) else (
    echo ✓ 已刪除所有容器
)
echo.

REM 清理選項
echo [3/3] 清理選項
echo.
echo 是否要執行完整清理（刪除未使用的映像、網路、卷）？
set /p clean="輸入 Y 執行完整清理，其他鍵跳過: "

if /i "%clean%"=="Y" (
    echo.
    echo ⚠ 警告：完整清理將刪除所有未使用的映像和卷！
    set /p cleanConfirm="確認執行完整清理？(輸入 YES 確認): "
    if /i "%cleanConfirm%"=="YES" (
        echo 正在執行完整清理...
        docker system prune -a -f --volumes >nul 2>&1
        echo ✓ 已執行完整清理
    ) else (
        echo 已跳過完整清理
    )
) else (
    echo 已跳過清理
)

echo.
echo ============================================
echo ✓ 卸載完成！
echo ============================================
echo.

REM 驗證結果
echo 驗證結果：
docker ps -a --format "{{.Names}}" 2>nul | findstr /V "^$" >nul
if errorlevel 1 (
    echo ✓ 所有容器已成功刪除
) else (
    echo ⚠ 仍有容器存在，請檢查
    docker ps -a
)

echo.
pause
