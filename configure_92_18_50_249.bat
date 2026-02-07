@echo off
REM 為92.18.50.249配置防火牆規則
REM Configure firewall rules for 92.18.50.249

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  配置防火牆規則 - 允許92.18.50.249連入                    ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM 首先移除舊的192.18.50.249規則
echo 🔄 清理舊規則 (192.18.50.249)...
netsh advfirewall firewall delete rule name="Allow-8069-192.18.50.249" dir=in >nul 2>&1
netsh advfirewall firewall delete rule name="Allow-8080-192.18.50.249" dir=in >nul 2>&1
netsh advfirewall firewall delete rule name="Allow-3001-192.18.50.249" dir=in >nul 2>&1
netsh advfirewall firewall delete rule name="Allow-80-192.18.50.249" dir=in >nul 2>&1
netsh advfirewall firewall delete rule name="Allow-443-192.18.50.249" dir=in >nul 2>&1
netsh advfirewall firewall delete rule name="Allow-5432-192.18.50.249" dir=in >nul 2>&1
echo ✅ 舊規則已清理

echo.
echo 📝 為92.18.50.249配置新規則...
echo.

REM Odoo (8069)
echo ⏳ 配置 Odoo (8069)...
netsh advfirewall firewall add rule name="Allow-Odoo-92.18.50.249" dir=in action=allow protocol=tcp localport=8069 remoteip=92.18.50.249 >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Odoo (8069) - 規則已添加
) else (
    echo ❌ Odoo (8069) - 配置失敗
)

REM AI Service (8080)
echo ⏳ 配置 AI Service (8080)...
netsh advfirewall firewall add rule name="Allow-AI-92.18.50.249" dir=in action=allow protocol=tcp localport=8080 remoteip=92.18.50.249 >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ AI Service (8080) - 規則已添加
) else (
    echo ❌ AI Service (8080) - 配置失敗
)

REM Uptime Kuma (3001)
echo ⏳ 配置 Uptime Kuma (3001)...
netsh advfirewall firewall add rule name="Allow-Kuma-92.18.50.249" dir=in action=allow protocol=tcp localport=3001 remoteip=92.18.50.249 >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Uptime Kuma (3001) - 規則已添加
) else (
    echo ❌ Uptime Kuma (3001) - 配置失敗
)

REM HTTP (80)
echo ⏳ 配置 HTTP (80)...
netsh advfirewall firewall add rule name="Allow-HTTP-92.18.50.249" dir=in action=allow protocol=tcp localport=80 remoteip=92.18.50.249 >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ HTTP (80) - 規則已添加
) else (
    echo ❌ HTTP (80) - 配置失敗
)

REM HTTPS (443)
echo ⏳ 配置 HTTPS (443)...
netsh advfirewall firewall add rule name="Allow-HTTPS-92.18.50.249" dir=in action=allow protocol=tcp localport=443 remoteip=92.18.50.249 >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ HTTPS (443) - 規則已添加
) else (
    echo ❌ HTTPS (443) - 配置失敗
)

REM PostgreSQL (5432)
echo ⏳ 配置 PostgreSQL (5432)...
netsh advfirewall firewall add rule name="Allow-PostgreSQL-92.18.50.249" dir=in action=allow protocol=tcp localport=5432 remoteip=92.18.50.249 >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ PostgreSQL (5432) - 規則已添加
) else (
    echo ❌ PostgreSQL (5432) - 配置失敗
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                    配置完成                               ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo ✅ 所有規則已為92.18.50.249配置完成
echo.
echo 📝 後續操作：
echo   1. 在PowerShell中執行驗證:
echo      .\test_external_ip_connection.ps1 -ExternalIP "92.18.50.249" -Action all
echo.
echo   2. 查看UI訪問:
echo      .\ui_access.ps1 -Service all
echo.

pause
