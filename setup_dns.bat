@echo off
REM DNS 快速設定腳本
REM 為商家和居民提供穩定服務可見度

echo ========================================
echo DNS 設定腳本 - 五常系統
echo ========================================
echo.

echo 步驟 1: 檢查 cloudflared 安裝...
cloudflared --version >nul 2>&1
if errorlevel 1 (
    echo [錯誤] cloudflared 未安裝
    echo 請先下載並安裝: https://github.com/cloudflare/cloudflared/releases
    pause
    exit /b 1
)
echo [OK] cloudflared 已安裝
echo.

echo 步驟 2: 登入 Cloudflare
echo 這會開啟瀏覽器讓您登入...
cloudflared tunnel login
if errorlevel 1 (
    echo [錯誤] 登入失敗
    pause
    exit /b 1
)
echo [OK] 登入成功
echo.

echo 步驟 3: 建立隧道
echo 請記下產生的 Tunnel ID...
cloudflared tunnel create wuchang-tunnel
if errorlevel 1 (
    echo [錯誤] 建立隧道失敗
    pause
    exit /b 1
)
echo [OK] 隧道建立成功
echo.

echo 步驟 4: 配置 DNS 路由
cloudflared tunnel route dns wuchang-tunnel app.wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel ai.wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel admin.wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel monitor.wuchang.org.tw
echo [OK] DNS 路由配置完成
echo.

echo 步驟 5: 請手動執行以下操作：
echo 1. 複製憑證檔案到 cloudflared\credentials.json
echo 2. 編輯 cloudflared\config.yml，更新 Tunnel ID
echo 3. 執行: docker restart wuchangv510-cloudflared-1
echo 4. 執行: python check_dns_status.py 驗證
echo.

pause
