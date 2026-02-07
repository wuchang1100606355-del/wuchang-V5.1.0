#!/usr/bin/env powershell
<#
.SYNOPSIS
    內網協調 + 外網握手 - 雙通道持續維持方案
    LAN Coordination + External Network Handshake - Dual Channel Keep-Alive
#>

param(
    [string]$LocalIP = "192.168.50.84",
    [string]$ExternalIP = "92.18.50.249",
    [int]$IntervalSeconds = 30
)

# 顏色配置
$colors = @{
    local_success = "Green"
    local_fail = "Yellow"
    external_success = "Cyan"
    external_fail = "Magenta"
    info = "Blue"
    header = "White"
    error = "Red"
}

function Log-LocalSuccess {
    param([string]$msg, [int]$port)
    Write-Host "[$(Get-Date -f 'HH:mm:ss')] ✅ 內網$msg (埤$port) 協調成功" -f $colors.local_success
}

function Log-LocalWarning {
    param([string]$msg, [int]$port)
    Write-Host "[$(Get-Date -f 'HH:mm:ss')] ⚠️  內網$msg (埤$port) 協調失敗" -f $colors.local_fail
}

function Log-ExternalSuccess {
    param([string]$msg, [int]$port)
    Write-Host "[$(Get-Date -f 'HH:mm:ss')] 🌐 外網$msg (埤$port) 握手成功" -f $colors.external_success
}

function Log-ExternalWarning {
    param([string]$msg, [int]$port)
    Write-Host "[$(Get-Date -f 'HH:mm:ss')] ⚠️  外網$msg (埤$port) 握手失敗" -f $colors.external_fail
}

function Log-Info {
    param([string]$msg)
    Write-Host "[$(Get-Date -f 'HH:mm:ss')] ℹ️  $msg" -f $colors.info
}

# 內網協調函數
function Test-LocalCoordination {
    param(
        [string]$Server,
        [int]$Port,
        [string]$ServiceName
    )
    
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.ConnectAsync($Server, $Port).Wait(2000) | Out-Null
        
        if ($tcp.Connected) {
            Log-LocalSuccess $ServiceName $Port
            $tcp.Close()
            return $true
        } else {
            Log-LocalWarning $ServiceName $Port
            return $false
        }
    } catch {
        Log-LocalWarning $ServiceName $Port
        return $false
    }
}

# 外網握手函數
function Test-ExternalHandshake {
    param(
        [string]$Server,
        [int]$Port,
        [string]$ServiceName
    )
    
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.ConnectAsync($Server, $Port).Wait(2000) | Out-Null
        
        if ($tcp.Connected) {
            Log-ExternalSuccess $ServiceName $Port
            $tcp.Close()
            return $true
        } else {
            Log-ExternalWarning $ServiceName $Port
            return $false
        }
    } catch {
        Log-ExternalWarning $ServiceName $Port
        return $false
    }
}

# =====================================================================
# 主程式
# =====================================================================

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════════════╗" -f $colors.header
Write-Host "║        內網協調 + 外網握手 - LAN Coordination + External Handshake  ║" -f $colors.header
Write-Host "║        內網IP: $LocalIP | 外網IP: $ExternalIP" -f $colors.header
Write-Host "║        每 $IntervalSeconds 秒同步一次 | Ctrl+C 停止                        ║" -f $colors.header
Write-Host "╚═══════════════════════════════════════════════════════════════════╝" -f $colors.header
Write-Host ""

# 服務配置
$services = @(
    @{ name = "Odoo"; port = 8069 }
    @{ name = "AI"; port = 8080 }
    @{ name = "Kuma"; port = 3001 }
    @{ name = "HTTP"; port = 80 }
    @{ name = "HTTPS"; port = 443 }
    @{ name = "PostgreSQL"; port = 5432 }
)

$cycle = 0
$running = $true
$localSuccess = @{}
$localFailure = @{}
$externalSuccess = @{}
$externalFailure = @{}

# 初始化計數器
foreach ($svc in $services) {
    $localSuccess[$svc.name] = 0
    $localFailure[$svc.name] = 0
    $externalSuccess[$svc.name] = 0
    $externalFailure[$svc.name] = 0
}

try {
    while ($running) {
        $cycle++
        Write-Host ""
        Write-Host ("═" * 73) -f $colors.info
        Log-Info "雙通道同步週期 #$cycle 開始"
        Write-Host ("═" * 73) -f $colors.info
        Write-Host ""
        
        $localCycleSuccess = 0
        $externalCycleSuccess = 0
        
        # 測試每個服務 (內網)
        Write-Host "📍 內網協調測試:" -f $colors.local_success
        foreach ($svc in $services) {
            if (Test-LocalCoordination -Server $LocalIP -Port $svc.port -ServiceName $svc.name) {
                $localSuccess[$svc.name]++
                $localCycleSuccess++
            } else {
                $localFailure[$svc.name]++
            }
        }
        
        Write-Host ""
        
        # 測試每個服務 (外網)
        Write-Host "🌍 外網握手測試:" -f $colors.external_success
        foreach ($svc in $services) {
            if (Test-ExternalHandshake -Server $ExternalIP -Port $svc.port -ServiceName $svc.name) {
                $externalSuccess[$svc.name]++
                $externalCycleSuccess++
            } else {
                $externalFailure[$svc.name]++
            }
        }
        
        Write-Host ""
        Write-Host "📊 本週期統計:" -f $colors.info
        Write-Host "   內網成功: $localCycleSuccess 個" -f $colors.local_success
        Write-Host "   外網成功: $externalCycleSuccess 個" -f $colors.external_success
        Write-Host ""
        
        # 顯示累計統計
        Write-Host "📈 累計統計 (前 $cycle 週期):" -f $colors.info
        Write-Host ""
        Write-Host "   內網成功率:" -f $colors.local_success
        foreach ($svc in $services) {
            $total = $localSuccess[$svc.name] + $localFailure[$svc.name]
            $rate = if ($total -gt 0) { [math]::Round($localSuccess[$svc.name] / $total * 100, 1) } else { 0 }
            Write-Host "      $($svc.name): $($localSuccess[$svc.name])/$total ($rate%)" -f $colors.local_success
        }
        
        Write-Host ""
        Write-Host "   外網成功率:" -f $colors.external_success
        foreach ($svc in $services) {
            $total = $externalSuccess[$svc.name] + $externalFailure[$svc.name]
            $rate = if ($total -gt 0) { [math]::Round($externalSuccess[$svc.name] / $total * 100, 1) } else { 0 }
            Write-Host "      $($svc.name): $($externalSuccess[$svc.name])/$total ($rate%)" -f $colors.external_success
        }
        
        Write-Host ""
        Log-Info "雙通道同步週期 #$cycle 完成"
        Log-Info "等待 $IntervalSeconds 秒後重試... (Ctrl+C 停止)"
        
        # 等待並監聽按鍵
        for ($i = $IntervalSeconds; $i -gt 0; $i--) {
            if ([Console]::KeyAvailable) {
                $key = [Console]::ReadKey($true)
                if ($key.Key -eq "C") {
                    $running = $false
                    break
                }
            }
            Start-Sleep -Milliseconds 100
        }
    }
} catch {
    Write-Host "[$(Get-Date -f 'HH:mm:ss')] ❌ 異常: $_" -f $colors.error
}

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════════════╗" -f $colors.error
Write-Host "║                   雙通道同步已停止                                  ║" -f $colors.error
Write-Host "╚═══════════════════════════════════════════════════════════════════╝" -f $colors.error
Write-Host ""

# 最終統計
Write-Host "📋 最終統計報告:" -f $colors.header
Write-Host ""
Write-Host "總同步週期: $cycle" -f $colors.info
Write-Host ""

Write-Host "✅ 內網協調結果:" -f $colors.local_success
foreach ($svc in $services) {
    $total = $localSuccess[$svc.name] + $localFailure[$svc.name]
    if ($total -gt 0) {
        $rate = [math]::Round($localSuccess[$svc.name] / $total * 100, 1)
        Write-Host "   $($svc.name): $($localSuccess[$svc.name])/$total (成功率: $rate%)" -f $colors.local_success
    }
}

Write-Host ""
Write-Host "🌐 外網握手結果:" -f $colors.external_success
foreach ($svc in $services) {
    $total = $externalSuccess[$svc.name] + $externalFailure[$svc.name]
    if ($total -gt 0) {
        $rate = [math]::Round($externalSuccess[$svc.name] / $total * 100, 1)
        if ($rate -eq 100) {
            Write-Host "   $($svc.name): $($externalSuccess[$svc.name])/$total (成功率: $rate%)" -f $colors.external_success
        } elseif ($rate -gt 0) {
            Write-Host "   $($svc.name): $($externalSuccess[$svc.name])/$total (成功率: $rate%)" -f $colors.external_fail
        } else {
            Write-Host "   $($svc.name): 0/$total (成功率: 0%)" -f $colors.error
        }
    }
}

Write-Host ""
