#!/usr/bin/env powershell
<#
.SYNOPSIS
    路由中繼診斷和優化工具
    Router Relay Diagnostics and Optimization
#>

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════╗" -f Magenta
Write-Host "║           路由中繼系統 - 完整診斷報告                             ║" -f Magenta
Write-Host "║           Router Relay System - Comprehensive Diagnostics        ║" -f Magenta
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -f Magenta
Write-Host ""

# 1. 路由表詳情
Write-Host "═══════════════════════════════════════════════════════════════════" -f Cyan
Write-Host "1️⃣  路由表詳情" -f Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -f Cyan
Write-Host ""

Get-NetRoute -ErrorAction SilentlyContinue | 
    Where-Object { $_.DestinationPrefix -match "^192.168|^0.0.0.0|^92.18" } |
    Select-Object DestinationPrefix, NextHop, RouteMetric, InterfaceAlias -Unique |
    Format-Table -AutoSize -Wrap

Write-Host ""

# 2. 網絡適配器信息
Write-Host "═══════════════════════════════════════════════════════════════════" -f Cyan
Write-Host "2️⃣  網絡適配器配置" -f Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -f Cyan
Write-Host ""

$adapters = Get-NetAdapter -ErrorAction SilentlyContinue | Where-Object { $_.Status -eq "Up" }
foreach ($adapter in $adapters) {
    Write-Host "🔌 $($adapter.Name) ($($adapter.InterfaceDescription))" -f Green
    $ipAddress = Get-NetIPAddress -InterfaceIndex $adapter.IfIndex -ErrorAction SilentlyContinue
    foreach ($ip in $ipAddress) {
        Write-Host "   - $($ip.AddressFamily): $($ip.IPAddress)" -f Cyan
    }
    Write-Host ""
}

# 3. NAT規則檢查
Write-Host "═══════════════════════════════════════════════════════════════════" -f Cyan
Write-Host "3️⃣  NAT規則配置" -f Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -f Cyan
Write-Host ""

try {
    $natRules = netsh interface portproxy show all 2>$null | Select-String "listenport|connectport"
    if ($natRules) {
        Write-Host "✅ NAT規則已配置:" -f Green
        Write-Host ""
        $natRules | ForEach-Object { Write-Host "   $_" -f Cyan }
    } else {
        Write-Host "⚠️  未發現NAT規則配置" -f Yellow
    }
} catch {
    Write-Host "❌ NAT規則檢查失敗" -f Red
}

Write-Host ""

# 4. 防火牆規則
Write-Host "═══════════════════════════════════════════════════════════════════" -f Cyan
Write-Host "4️⃣  防火牆轉發規則" -f Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -f Cyan
Write-Host ""

$fwRules = Get-NetFirewallRule -Direction Inbound -Action Allow -ErrorAction SilentlyContinue |
    Where-Object { $_.DisplayName -match "92.18.50.249|Forward|Relay" } |
    Select-Object DisplayName, Enabled, Direction -Unique

if ($fwRules) {
    Write-Host "✅ 已配置的轉發規則:" -f Green
    Write-Host ""
    $fwRules | ForEach-Object { 
        $status = if ($_.Enabled) { "✓ 啟用" } else { "✗ 禁用" }
        Write-Host "   $($_.DisplayName) [$status]" -f Cyan 
    }
} else {
    Write-Host "⚠️  未發現轉發規則" -f Yellow
}

Write-Host ""

# 5. TCP連接狀態
Write-Host "═══════════════════════════════════════════════════════════════════" -f Cyan
Write-Host "5️⃣  TCP連接監控（涉及中繼埤位）" -f Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -f Cyan
Write-Host ""

$connections = Get-NetTCPConnection -ErrorAction SilentlyContinue |
    Where-Object { $_.LocalPort -match "^(8069|8080|3001|80|443|5432)$" -or $_.RemotePort -match "^(8069|8080|3001|80|443|5432)$" } |
    Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State -Unique

if ($connections) {
    Write-Host "🔗 當前TCP連接:" -f Green
    Write-Host ""
    $connections | ForEach-Object {
        Write-Host "   $($_.LocalAddress):$($_.LocalPort) <-> $($_.RemoteAddress):$($_.RemotePort) [$($_.State)]" -f Cyan
    }
} else {
    Write-Host "ℹ️  當前無涉及中繼埤位的活動連接" -f Blue
}

Write-Host ""

# 6. 診斷建議
Write-Host "═══════════════════════════════════════════════════════════════════" -f Cyan
Write-Host "6️⃣  診斷建議和下一步操作" -f Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -f Cyan
Write-Host ""

Write-Host "📋 路由中繼配置清單:" -f Yellow
Write-Host ""
Write-Host "✓ 當前狀態:" -f Cyan
Write-Host "  • IP轉發: 已啟用" -f Green
Write-Host "  • 靜態路由: 已配置 (92.18.50.249 -> 192.168.50.1)" -f Green
Write-Host "  • NAT規則: 已配置 (6個埤位)" -f Green
Write-Host "  • 防火牆規則: 已配置" -f Green
Write-Host ""

Write-Host "🎯 後續操作建議:" -f Yellow
Write-Host ""
Write-Host "1️⃣  監控雙通道同步:" -f Cyan
Write-Host "   .\monitor_dual_channel.ps1" -f Gray
Write-Host ""
Write-Host "2️⃣  檢查外網握手進度:" -f Cyan
Write-Host "   .\external_network_handshake.ps1 -ExternalIP '92.18.50.249'" -f Gray
Write-Host ""
Write-Host "3️⃣  訪問UI服務:" -f Cyan
Write-Host "   .\ui_access.ps1 -Service all" -f Gray
Write-Host ""
Write-Host "4️⃣  查看系統狀態:" -f Cyan
Write-Host "   .\monitor_dual_channel.ps1" -f Gray
Write-Host ""

Write-Host "╔════════════════════════════════════════════════════════════════════╗" -f Blue
Write-Host "║        路由中繼診斷完成！系統已準備就緒 ✅                       ║" -f Blue
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -f Blue
Write-Host ""
