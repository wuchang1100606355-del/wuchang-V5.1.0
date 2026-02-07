#!/usr/bin/env powershell
<#
.SYNOPSIS
    Wuchang 系統實時監控面板 - 內網協調 + 外網握手狀態
#>

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════╗" -f Cyan
Write-Host "║          Wuchang 雙通道同步系統 - 實時監控面板                    ║" -f Cyan
Write-Host "║          LAN Coordination + External Handshake Monitor             ║" -f Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -f Cyan
Write-Host ""

Write-Host "🎯 當前運行狀態:" -f Yellow
Write-Host ""

# 檢查進程
$dualProcess = Get-Process | Where-Object { $_.Name -match "powershell|pwsh" -and $_.CommandLine -match "dual_channel_synchronization" } | Select-Object -First 1

if ($dualProcess) {
    Write-Host "✅ 雙通道同步進程: 運行中" -f Green
    Write-Host "   進程ID: $($dualProcess.Id)" -f Cyan
    Write-Host "   進程名稱: $($dualProcess.Name)" -f Cyan
} else {
    Write-Host "⚠️  雙通道同步進程: 未運行" -f Yellow
}

Write-Host ""

# 檢查握手進程
$handshakeProcess = Get-Process | Where-Object { $_.Name -match "powershell|pwsh" -and $_.CommandLine -match "external_network_handshake" } | Select-Object -First 1

if ($handshakeProcess) {
    Write-Host "✅ 外網握手進程: 運行中" -f Cyan
    Write-Host "   進程ID: $($handshakeProcess.Id)" -f Cyan
} else {
    Write-Host "⚠️  外網握手進程: 未運行" -f Magenta
}

Write-Host ""

# 檢查本機服務狀態
Write-Host "📊 本機服務監控:" -f Yellow
Write-Host ""

$ports = @(
    @{ name = "Odoo"; port = 8069; ip = "localhost" }
    @{ name = "AI"; port = 8080; ip = "localhost" }
    @{ name = "Kuma"; port = 3001; ip = "localhost" }
    @{ name = "HTTP"; port = 80; ip = "localhost" }
    @{ name = "HTTPS"; port = 443; ip = "localhost" }
    @{ name = "PostgreSQL"; port = 5432; ip = "localhost" }
)

foreach ($svc in $ports) {
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $task = $tcp.ConnectAsync($svc.ip, $svc.port)
        if ($task.Wait(1000)) {
            Write-Host "   ✅ $($svc.name) (埤$($svc.port)): 運行中" -f Green
            $tcp.Close()
        } else {
            Write-Host "   ⚠️  $($svc.name) (埤$($svc.port)): 無回應" -f Yellow
        }
    } catch {
        Write-Host "   ❌ $($svc.name) (埤$($svc.port)): 離線" -f Red
    }
}

Write-Host ""

# 檢查防火牆規則
Write-Host "🔥 防火牆規則檢查:" -f Yellow
Write-Host ""

$rules = Get-NetFirewallRule -Direction Inbound -Action Allow -ErrorAction SilentlyContinue | 
    Where-Object { $_.DisplayName -match "92.18.50.249" }

Write-Host "   針對92.18.50.249的入站規則: $($rules.Count)條" -f Cyan

if ($rules.Count -gt 0) {
    foreach ($rule in $rules) {
        Write-Host "      ✓ $($rule.DisplayName)" -f Green
    }
} else {
    Write-Host "      ⚠️  未發現規則，請運行配置腳本" -f Yellow
}

Write-Host ""

# 檢查網絡連接
Write-Host "🌐 網絡連接狀態:" -f Yellow
Write-Host ""

# 本機IP
$localIP = ipconfig | Select-String "IPv4 Address" | Select-Object -First 1 | ForEach-Object { $_.ToString().Split(":")[1].Trim() }
Write-Host "   本機IP (LAN): $localIP" -f Cyan

# IPv6
$ipv6 = ipconfig | Select-String "IPv6 Address" | Select-Object -First 1 | ForEach-Object { $_.ToString().Split(":")[1].Trim() }
if ($ipv6) {
    Write-Host "   IPv6地址: $ipv6" -f Cyan
}

Write-Host ""

# 操作建議
Write-Host "📋 後續操作:" -f Yellow
Write-Host ""

if (!$dualProcess) {
    Write-Host "1️⃣  啟動雙通道同步:" -f Yellow
    Write-Host "    .\dual_channel_synchronization.ps1 -IntervalSeconds 30" -f Cyan
    Write-Host ""
}

Write-Host "2️⃣  查看握手進度:" -f Yellow
Write-Host "    .\external_network_handshake.ps1 -ExternalIP '92.18.50.249' -IntervalSeconds 30" -f Cyan
Write-Host ""

Write-Host "3️⃣  測試外網連接:" -f Yellow
Write-Host "    .\test_external_ip_connection.ps1 -ExternalIP '92.18.50.249' -Action all" -f Cyan
Write-Host ""

Write-Host "4️⃣  訪問UI服務:" -f Yellow
Write-Host "    .\ui_access.ps1 -Service all" -f Cyan
Write-Host ""

Write-Host "╔════════════════════════════════════════════════════════════════════╗" -f Blue
Write-Host "║                   系統就緒！可以開始工作了 🎉                     ║" -f Blue
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -f Blue
Write-Host ""
