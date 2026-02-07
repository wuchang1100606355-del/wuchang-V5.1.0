#!/usr/bin/env pwsh
<#
.SYNOPSIS
    伺服器健康監控與自動喚醒
.DESCRIPTION
    定期檢查伺服器狀態，如果離線自動喚醒
#>

param(
    [string]$ServerIP = "192.168.50.84",
    [string]$ServerMAC = "",
    [int]$CheckInterval = 300,
    [int]$OfflineThreshold = 3,
    [string]$LogFile = "$PSScriptRoot\server_watchdog.log",
    [switch]$RunOnce
)

$colors = @{ ok = "Green"; warn = "Yellow"; err = "Red"; info = "Cyan"; header = "Magenta" }
function H($t) { Write-Host "`n$('═'*70)" -f $colors.header; Write-Host "  $t" -f $colors.header; Write-Host $('═'*70) -f $colors.header }
function OK($m) { Write-Host "  [OK]   $m" -f $colors.ok; Log-Message "OK: $m" }
function WW($m) { Write-Host "  [WARN] $m" -f $colors.warn; Log-Message "WARN: $m" }
function EE($m) { Write-Host "  [ERR]  $m" -f $colors.err; Log-Message "ERR: $m" }
function II($m) { Write-Host "  [INFO] $m" -f $colors.info; Log-Message "INFO: $m" }

function Log-Message {
    param([string]$msg)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "[$timestamp] $msg" | Out-File -FilePath $LogFile -Append -Encoding UTF8
}

H "伺服器健康監控 - Server Watchdog"
II "監控目標: $ServerIP"
II "檢查間隔: $CheckInterval 秒"
II "離線閾值: $OfflineThreshold 次"
II "日誌檔案: $LogFile"

# 自動偵測 MAC（如果未提供）
if ([string]::IsNullOrEmpty($ServerMAC)) {
    II "嘗試偵測伺服器 MAC 地址..."
    
    try {
        $null = Test-Connection -ComputerName $ServerIP -Count 1 -ErrorAction SilentlyContinue
        $arpResult = arp -a $ServerIP 2>$null | Select-String $ServerIP
        if ($arpResult) {
            $macMatch = $arpResult -match '([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})'
            if ($macMatch) {
                $ServerMAC = $matches[0].Replace('-', ':')
                OK "偵測到 MAC: $ServerMAC"
            }
        }
    } catch {}
    
    if ([string]::IsNullOrEmpty($ServerMAC)) {
        WW "無法自動偵測 MAC，將無法執行喚醒"
        II "請手動指定: -ServerMAC 'AA:BB:CC:DD:EE:FF'"
    }
}

# 狀態追蹤
$consecutiveFailures = 0
$totalChecks = 0
$totalOffline = 0
$totalWakeups = 0
$lastWakeupTime = $null

# 檢查函數
function Test-ServerHealth {
    $totalChecks++
    
    # 方法 1: Ping
    $pingSuccess = Test-Connection -ComputerName $ServerIP -Count 2 -Quiet -ErrorAction SilentlyContinue
    
    # 方法 2: SSH port (22)
    $sshSuccess = $false
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $task = $tcp.ConnectAsync($ServerIP, 22)
        if ($task.Wait(3000)) {
            $sshSuccess = $tcp.Connected
            $tcp.Close()
        }
    } catch {}
    
    # 方法 3: HTTP port (80)
    $httpSuccess = $false
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $task = $tcp.ConnectAsync($ServerIP, 80)
        if ($task.Wait(3000)) {
            $httpSuccess = $tcp.Connected
            $tcp.Close()
        }
    } catch {}
    
    $isOnline = $pingSuccess -or $sshSuccess -or $httpSuccess
    
    return @{
        Online = $isOnline
        Ping = $pingSuccess
        SSH = $sshSuccess
        HTTP = $httpSuccess
        Timestamp = Get-Date
    }
}

# 喚醒函數
function Invoke-ServerWakeup {
    if ([string]::IsNullOrEmpty($ServerMAC)) {
        EE "無法喚醒：未知 MAC 地址"
        return $false
    }
    
    WW "執行伺服器喚醒..."
    
    try {
        $wakeScript = Join-Path $PSScriptRoot "wake_server.ps1"
        if (Test-Path $wakeScript) {
            & $wakeScript -MAC $ServerMAC -ServerIP $ServerIP -Retries 2
            $script:totalWakeups++
            $script:lastWakeupTime = Get-Date
            return $LASTEXITCODE -eq 0
        } else {
            EE "找不到 wake_server.ps1"
            return $false
        }
    } catch {
        EE "喚醒失敗: $_"
        return $false
    }
}

# 主監控迴圈
$running = $true

Write-Host ""
II "開始監控... (Ctrl+C 停止)"
Write-Host ""

try {
    while ($running) {
        $status = Test-ServerHealth
        
        $statusSymbol = if ($status.Online) { "✓" } else { "✗" }
        $statusColor = if ($status.Online) { $colors.ok } else { $colors.err }
        
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] " -NoNewline
        Write-Host "$statusSymbol $ServerIP " -NoNewline -f $statusColor
        Write-Host "| Ping:$($status.Ping) SSH:$($status.SSH) HTTP:$($status.HTTP) " -NoNewline -f $colors.info
        Write-Host "| 失敗:$consecutiveFailures/$OfflineThreshold" -f $colors.info
        
        if ($status.Online) {
            if ($consecutiveFailures -gt 0) {
                OK "伺服器已恢復上線"
            }
            $consecutiveFailures = 0
        } else {
            $consecutiveFailures++
            $totalOffline++
            
            if ($consecutiveFailures -ge $OfflineThreshold) {
                WW "伺服器已離線 $consecutiveFailures 次，觸發喚醒"
                
                # 檢查是否剛喚醒過（避免頻繁喚醒）
                if ($null -ne $lastWakeupTime) {
                    $timeSinceWakeup = (Get-Date) - $lastWakeupTime
                    if ($timeSinceWakeup.TotalSeconds -lt 300) {
                        WW "上次喚醒僅 $([int]$timeSinceWakeup.TotalSeconds) 秒前，跳過"
                        $consecutiveFailures = 0
                        continue
                    }
                }
                
                if (Invoke-ServerWakeup) {
                    OK "喚醒訊號已發送"
                    $consecutiveFailures = 0
                    
                    # 等待啟動
                    II "等待 60 秒讓伺服器啟動..."
                    Start-Sleep -Seconds 60
                } else {
                    EE "喚醒失敗"
                }
            }
        }
        
        # 統計資訊
        if ($totalChecks % 12 -eq 0) {
            Write-Host ""
            II "累計統計: 檢查 $totalChecks 次 | 離線 $totalOffline 次 | 喚醒 $totalWakeups 次"
            Write-Host ""
        }
        
        if ($RunOnce) {
            break
        }
        
        # 等待下次檢查
        Start-Sleep -Seconds $CheckInterval
    }
} catch {
    EE "監控異常: $_"
} finally {
    H "監控已停止"
    Write-Host ""
    Write-Host "  總檢查次數: $totalChecks" -f $colors.info
    Write-Host "  離線次數: $totalOffline" -f $colors.warn
    Write-Host "  喚醒次數: $totalWakeups" -f $colors.info
    Write-Host "  日誌檔案: $LogFile" -f $colors.info
    Write-Host ""
}
