#!/usr/bin/env powershell
<#
.SYNOPSIS
    為92.18.50.249配置防火牆規則
#>

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -f Cyan
Write-Host "║  為92.18.50.249配置防火牆規則                             ║" -f Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -f Cyan
Write-Host ""

$ip = "92.18.50.249"

# 配置AI (8080)
Write-Host "配置 AI (8080)..." -f Yellow
cmd /c "netsh advfirewall firewall delete rule name='Allow-AI-92.18.50.249' dir=in" 2>$null | Out-Null
cmd /c "netsh advfirewall firewall add rule name='Allow-AI-92.18.50.249' dir=in action=allow protocol=tcp localport=8080 remoteip=$ip" | Out-Null
Write-Host "✅ AI (8080) 規則已配置" -f Green
Write-Host ""

# 配置Kuma (3001)
Write-Host "配置 Kuma (3001)..." -f Yellow
cmd /c "netsh advfirewall firewall delete rule name='Allow-Kuma-92.18.50.249' dir=in" 2>$null | Out-Null
cmd /c "netsh advfirewall firewall add rule name='Allow-Kuma-92.18.50.249' dir=in action=allow protocol=tcp localport=3001 remoteip=$ip" | Out-Null
Write-Host "✅ Kuma (3001) 規則已配置" -f Green
Write-Host ""

# 配置HTTP (80)
Write-Host "配置 HTTP (80)..." -f Yellow
cmd /c "netsh advfirewall firewall delete rule name='Allow-HTTP-92.18.50.249' dir=in" 2>$null | Out-Null
cmd /c "netsh advfirewall firewall add rule name='Allow-HTTP-92.18.50.249' dir=in action=allow protocol=tcp localport=80 remoteip=$ip" | Out-Null
Write-Host "✅ HTTP (80) 規則已配置" -f Green
Write-Host ""

# 配置HTTPS (443)
Write-Host "配置 HTTPS (443)..." -f Yellow
cmd /c "netsh advfirewall firewall delete rule name='Allow-HTTPS-92.18.50.249' dir=in" 2>$null | Out-Null
cmd /c "netsh advfirewall firewall add rule name='Allow-HTTPS-92.18.50.249' dir=in action=allow protocol=tcp localport=443 remoteip=$ip" | Out-Null
Write-Host "✅ HTTPS (443) 規則已配置" -f Green
Write-Host ""

# 配置PostgreSQL (5432)
Write-Host "配置 PostgreSQL (5432)..." -f Yellow
cmd /c "netsh advfirewall firewall delete rule name='Allow-PostgreSQL-92.18.50.249' dir=in" 2>$null | Out-Null
cmd /c "netsh advfirewall firewall add rule name='Allow-PostgreSQL-92.18.50.249' dir=in action=allow protocol=tcp localport=5432 remoteip=$ip" | Out-Null
Write-Host "✅ PostgreSQL (5432) 規則已配置" -f Green
Write-Host ""

Write-Host "╔════════════════════════════════════════════════════════════╗" -f Green
Write-Host "║              ✅ 所有規則配置完成！                        ║" -f Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -f Green
Write-Host ""
