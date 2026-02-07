@echo off
REM =====================================================================
REM Wuchang 防火牆配置 - 為 192.18.50.249 開放連入
REM =====================================================================

setlocal enabledelayedexpansion

set "TARGET_IP=192.18.50.249"
set "PORTS=8069 8080 3001 80 443 5432"

echo.
echo ╔═══════════════════════════════════════════════════════════════════╗
echo ║  Wuchang 防火牆配置 - 開放 IP 192.18.50.249 連入                 ║
echo ╚═══════════════════════════════════════════════════════════════════╝
echo.

echo 【步驟 1】移除舊規則...
for %%P in (%PORTS%) do (
    netsh advfirewall firewall delete rule name="Allow-%%P-%TARGET_IP%" >nul 2>&1
)

echo 【步驟 2】添加新入站規則...
for %%P in (%PORTS%) do (
    echo   • 配置埤 %%P...
    netsh advfirewall firewall add rule ^
        name="Allow-%%P-%TARGET_IP%" ^
        dir=in action=allow ^
        protocol=tcp localport=%%P ^
        remoteip=%TARGET_IP% ^
        description="Allow %TARGET_IP% to access port %%P"
)

echo.
echo 【步驟 3】驗證規則...
netsh advfirewall firewall show rule name="Allow-*-%TARGET_IP%"

echo.
echo ✅ 防火牆配置完成！
echo    IP 192.18.50.249 現可連入本機所有主要服務埤
echo.
pause
