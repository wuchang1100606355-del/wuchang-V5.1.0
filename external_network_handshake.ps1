#!/usr/bin/env powershell
<#
.SYNOPSIS
    外網握手信號測試 - 模擬外網IP進行握手
    External Network Handshake Test - Simulate external IP handshake
#>

param(
    [string]$ExternalIP = "92.18.50.249",
    [int]$IntervalSeconds = 30
)

# 顏色配置
$colors = @{
    success = "Green"
    warning = "Yellow"
    error = "Red"
    info = "Cyan"
    header = "Magenta"
}

function Log-Success {
    param([string]$msg, [int]$port)
    Write-Host "[$(Get-Date -f 'HH:mm:ss')] ✅ $msg (埤$port) 握手成功" -f $colors.success
}

function Log-Warning {
    param([string]$msg, [int]$port)
    Write-Host "[$(Get-Date -f 'HH:mm:ss')] ⚠️  $msg (埤$port) 握手失敗" -f $colors.warning
}

function Log-Error {
    param([string]$msg)
    Write-Host "[$(Get-Date -f 'HH:mm:ss')] ❌ $msg" -f $colors.error
}

function Log-Info {
    param([string]$msg)
    Write-Host "[$(Get-Date -f 'HH:mm:ss')] ℹ️  $msg" -f $colors.info
}

# 外網握手函數
function Test-ExternalHandshake {
    param(
        [string]$Server,
        [int]$Port,
        [string]$ServiceName,
        [string]$TestType = "TCP"
    )
    
    try {
        if ($TestType -eq "TCP") {
            $tcp = New-Object System.Net.Sockets.TcpClient
            $tcp.ConnectAsync($Server, $Port).Wait(3000) | Out-Null
            
            if ($tcp.Connected) {
                Log-Success $ServiceName $Port
                $tcp.Close()
                return $true
            } else {
                Log-Warning $ServiceName $Port
                return $false
            }
        }
        elseif ($TestType -eq "HTTP") {
            try {
                $result = Invoke-WebRequest -Uri "http://$Server`:$Port" -TimeoutSec 3 -UseBasicParsing -Method Head -ErrorAction SilentlyContinue
                if ($result.StatusCode -eq 200) {
                    Log-Success $ServiceName $Port
                    return $true
                }
            } catch {}
            Log-Warning $ServiceName $Port
            return $false
        }
    } catch {
        Log-Warning $ServiceName $Port
        return $false
    }
}

# =====================================================================
# 主程式
# =====================================================================

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════════════╗" -f $colors.header
Write-Host "║           外網握手信號測試 - External Network Handshake          ║" -f $colors.header
Write-Host "║           外網IP: $ExternalIP" -f $colors.header
Write-Host "║           每 $IntervalSeconds 秒握手一次 | Ctrl+C 停止                        ║" -f $colors.header
Write-Host "╚═══════════════════════════════════════════════════════════════════╝" -f $colors.header
Write-Host ""

# 服務配置
$services = @(
    @{ name = "Odoo"; port = 8069; type = "TCP" }
    @{ name = "AI"; port = 8080; type = "TCP" }
    @{ name = "Kuma"; port = 3001; type = "TCP" }
    @{ name = "HTTP"; port = 80; type = "HTTP" }
    @{ name = "HTTPS"; port = 443; type = "TCP" }
    @{ name = "PostgreSQL"; port = 5432; type = "TCP" }
)

$cycle = 0
$running = $true
$successCount = @{}
$failureCount = @{}

# 初始化計數器
foreach ($svc in $services) {
    $successCount[$svc.name] = 0
    $failureCount[$svc.name] = 0
}

try {
    while ($running) {
        $cycle++
        Write-Host ""
        Write-Host ("═" * 73) -f $colors.info
        Log-Info "握手週期 #$cycle 開始"
        Write-Host ("═" * 73) -f $colors.info
        Write-Host ""
        
        $cycleSuccess = 0
        $cycleFailure = 0
        
        # 測試每個服務
        foreach ($svc in $services) {
            if (Test-ExternalHandshake -Server $ExternalIP -Port $svc.port -ServiceName $svc.name -TestType $svc.type) {
                $successCount[$svc.name]++
                $cycleSuccess++
            } else {
                $failureCount[$svc.name]++
                $cycleFailure++
            }
        }
        
        Write-Host ""
        Write-Host "📊 本週期統計:" -f $colors.info
        Write-Host "   成功: $cycleSuccess 個" -f $colors.success
        Write-Host "   失敗: $cycleFailure 個" -f $colors.warning
        Write-Host ""
        
        # 顯示累計統計
        Write-Host "📈 累計統計 (前 $cycle 週期):" -f $colors.info
        foreach ($svc in $services) {
            $total = $successCount[$svc.name] + $failureCount[$svc.name]
            $successRate = if ($total -gt 0) { [math]::Round($successCount[$svc.name] / $total * 100, 1) } else { 0 }
            Write-Host "   $($svc.name): $($successCount[$svc.name])成功 / $($failureCount[$svc.name])失敗 (成功率: $successRate%)" -f $colors.info
        }
        
        Write-Host ""
        Log-Info "握手週期 #$cycle 完成"
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
    Log-Error "握手異常: $_"
}

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════════════╗" -f $colors.error
Write-Host "║                   握手信號已停止                                  ║" -f $colors.error
Write-Host "╚═══════════════════════════════════════════════════════════════════╝" -f $colors.error
Write-Host ""

# 最終統計
Write-Host "📋 最終統計報告:" -f $colors.header
Write-Host ""
Write-Host "總握手週期: $cycle" -f $colors.info
Write-Host ""

foreach ($svc in $services) {
    $total = $successCount[$svc.name] + $failureCount[$svc.name]
    if ($total -gt 0) {
        $successRate = [math]::Round($successCount[$svc.name] / $total * 100, 1)
        if ($successRate -eq 100) {
            Write-Host "✅ $($svc.name): $($successCount[$svc.name])/$total (成功率: $successRate%)" -f $colors.success
        } elseif ($successRate -gt 0) {
            Write-Host "⚠️  $($svc.name): $($successCount[$svc.name])/$total (成功率: $successRate%)" -f $colors.warning
        } else {
            Write-Host "❌ $($svc.name): $($successCount[$svc.name])/$total (成功率: $successRate%)" -f $colors.error
        }
    }
}

Write-Host ""
Write-Host "📝 診斷建議:" -f $colors.header
Write-Host "   1. 檢查防火牆規則: .\verify_ip_allowlist.ps1 -Action all" -f $colors.info
Write-Host "   2. 檢查本機服務: .\test_external_ip_connection.ps1 -Action status" -f $colors.info
Write-Host "   3. 查看詳細配置: .\test_external_ip_connection.ps1 -ExternalIP '92.18.50.249' -Action firewall" -f $colors.info
Write-Host ""
