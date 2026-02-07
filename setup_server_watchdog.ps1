#!/usr/bin/env pwsh
<#
.SYNOPSIS
    設定伺服器健康監控排程
.DESCRIPTION
    建立 Windows Task 定期監控伺服器並在離線時自動喚醒
#>

param(
    [string]$ServerIP = "192.168.50.84",
    [string]$ServerMAC = "",
    [int]$CheckInterval = 300,
    [string]$TaskName = "WuchangServerWatchdog",
    [ValidateSet("Install", "Uninstall", "Status", "Test")]
    [string]$Action = "Install"
)

$colors = @{ ok = "Green"; warn = "Yellow"; err = "Red"; info = "Cyan"; header = "Magenta" }
function H($t) { Write-Host "`n$('═'*70)" -f $colors.header; Write-Host "  $t" -f $colors.header; Write-Host $('═'*70) -f $colors.header }
function OK($m) { Write-Host "  [OK]   $m" -f $colors.ok }
function WW($m) { Write-Host "  [WARN] $m" -f $colors.warn }
function EE($m) { Write-Host "  [ERR]  $m" -f $colors.err }
function II($m) { Write-Host "  [INFO] $m" -f $colors.info }

H "伺服器監控排程管理"

# 檢查管理員權限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

switch ($Action) {
    "Test" {
        H "測試監控功能"
        
        $monitorScript = "$PSScriptRoot\monitor_server_health.ps1"
        if (-not (Test-Path $monitorScript)) {
            EE "找不到監控腳本: $monitorScript"
            exit 1
        }
        
        II "執行一次性檢查..."
        $args = @(
            "-ServerIP", $ServerIP,
            "-CheckInterval", "10",
            "-OfflineThreshold", "2",
            "-RunOnce"
        )
        
        if (-not [string]::IsNullOrEmpty($ServerMAC)) {
            $args += "-ServerMAC", $ServerMAC
        }
        
        & $monitorScript @args
    }
    
    "Status" {
        if (-not $isAdmin) {
            WW "查看完整狀態需要管理員權限"
        }
        
        H "檢查排程狀態"
        
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($task) {
            OK "排程已存在"
            Write-Host ""
            Write-Host "  任務名稱: $($task.TaskName)" -f $colors.info
            Write-Host "  狀態: $($task.State)" -f $colors.info
            
            $info = Get-ScheduledTaskInfo -TaskName $TaskName -ErrorAction SilentlyContinue
            if ($info) {
                Write-Host ""
                Write-Host "  最後執行: $($info.LastRunTime)" -f $colors.info
                Write-Host "  最後結果: $($info.LastTaskResult)" -f $colors.info
                Write-Host "  下次執行: $($info.NextRunTime)" -f $colors.info
            }
            
            # 顯示日誌
            $logFile = "$PSScriptRoot\server_watchdog.log"
            if (Test-Path $logFile) {
                Write-Host ""
                II "最近日誌 (最後 10 行):"
                Get-Content $logFile -Tail 10 | ForEach-Object {
                    Write-Host "    $_" -f $colors.info
                }
            }
        } else {
            WW "排程不存在"
            II "使用 -Action Install 安裝排程"
        }
    }
    
    "Uninstall" {
        if (-not $isAdmin) {
            EE "需要系統管理員權限"
            exit 1
        }
        
        H "移除排程"
        
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($task) {
            try {
                # 停止執行中的任務
                Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
                
                # 移除排程
                Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
                OK "排程已移除"
            } catch {
                EE "移除失敗: $_"
                exit 1
            }
        } else {
            WW "排程不存在"
        }
    }
    
    "Install" {
        if (-not $isAdmin) {
            EE "需要系統管理員權限"
            II "請以系統管理員身分執行 PowerShell"
            exit 1
        }
        
        H "安裝監控排程"
        
        # 檢查腳本
        $monitorScript = "$PSScriptRoot\monitor_server_health.ps1"
        if (-not (Test-Path $monitorScript)) {
            EE "找不到監控腳本: $monitorScript"
            exit 1
        }
        OK "監控腳本: $monitorScript"
        
        # 嘗試偵測 MAC（如果未提供）
        if ([string]::IsNullOrEmpty($ServerMAC)) {
            II "嘗試偵測伺服器 MAC..."
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
                WW "無法偵測 MAC 地址"
                $inputMAC = Read-Host "請輸入伺服器 MAC 地址 (格式: AA:BB:CC:DD:EE:FF，留空跳過)"
                if (-not [string]::IsNullOrEmpty($inputMAC)) {
                    $ServerMAC = $inputMAC
                } else {
                    WW "未設定 MAC，將無法自動喚醒伺服器"
                }
            }
        }
        
        # 移除舊排程
        $existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($existing) {
            WW "發現舊排程，將先移除"
            Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
            Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        }
        
        # 建立動作
        $pwshPath = (Get-Command pwsh -ErrorAction SilentlyContinue).Source
        if (-not $pwshPath) {
            $pwshPath = "powershell.exe"
            WW "找不到 pwsh，使用 powershell.exe"
        }
        
        $arguments = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$monitorScript`" -ServerIP `"$ServerIP`" -CheckInterval $CheckInterval -OfflineThreshold 3"
        if (-not [string]::IsNullOrEmpty($ServerMAC)) {
            $arguments += " -ServerMAC `"$ServerMAC`""
        }
        
        $action = New-ScheduledTaskAction -Execute $pwshPath -Argument $arguments
        
        # 建立觸發器（開機後 5 分鐘啟動，持續執行）
        $trigger = New-ScheduledTaskTrigger -AtStartup
        $trigger.Delay = "PT5M"
        
        # 建立設定
        $settings = New-ScheduledTaskSettingsSet `
            -AllowStartIfOnBatteries `
            -DontStopIfGoingOnBatteries `
            -DontStopOnIdleEnd `
            -StartWhenAvailable `
            -RunOnlyIfNetworkAvailable `
            -ExecutionTimeLimit ([TimeSpan]::Zero) `
            -RestartCount 3 `
            -RestartInterval (New-TimeSpan -Minutes 5)
        
        # 建立主體
        $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest
        
        # 註冊排程
        try {
            Register-ScheduledTask `
                -TaskName $TaskName `
                -Action $action `
                -Trigger $trigger `
                -Settings $settings `
                -Principal $principal `
                -Description "五常 AI - 伺服器健康監控與自動喚醒 (檢查間隔: $CheckInterval 秒)" `
                -ErrorAction Stop | Out-Null
            
            OK "排程已建立"
            Write-Host ""
            Write-Host "  任務名稱: $TaskName" -f $colors.info
            Write-Host "  監控目標: $ServerIP" -f $colors.info
            if (-not [string]::IsNullOrEmpty($ServerMAC)) {
                Write-Host "  MAC 地址: $ServerMAC" -f $colors.info
            }
            Write-Host "  檢查間隔: $CheckInterval 秒" -f $colors.info
            Write-Host "  啟動時機: 開機後 5 分鐘" -f $colors.info
            Write-Host "  執行帳戶: $env:USERNAME (提升權限)" -f $colors.info
            
        } catch {
            EE "建立排程失敗: $_"
            exit 1
        }
        
        # 立即啟動測試
        H "啟動監控"
        $confirm = Read-Host "是否立即啟動監控? (y/N)"
        if ($confirm -eq "y" -or $confirm -eq "Y") {
            II "啟動排程任務..."
            Start-ScheduledTask -TaskName $TaskName
            OK "監控已啟動"
            II "查看日誌: Get-Content '$PSScriptRoot\server_watchdog.log' -Tail 20 -Wait"
        } else {
            II "將在下次開機後自動啟動"
        }
    }
}

# 管理指令
H "管理指令"
Write-Host ""
Write-Host "  查看狀態:" -f $colors.info
Write-Host "    pwsh -File .\setup_server_watchdog.ps1 -Action Status" -f $colors.header
Write-Host ""
Write-Host "  測試監控 (執行一次):" -f $colors.info
Write-Host "    pwsh -File .\setup_server_watchdog.ps1 -Action Test" -f $colors.header
Write-Host ""
Write-Host "  手動啟動排程:" -f $colors.info
Write-Host "    Start-ScheduledTask -TaskName '$TaskName'" -f $colors.header
Write-Host ""
Write-Host "  停止排程:" -f $colors.info
Write-Host "    Stop-ScheduledTask -TaskName '$TaskName'" -f $colors.header
Write-Host ""
Write-Host "  即時查看日誌:" -f $colors.info
Write-Host "    Get-Content '$PSScriptRoot\server_watchdog.log' -Tail 20 -Wait" -f $colors.header
Write-Host ""
Write-Host "  移除排程:" -f $colors.info
Write-Host "    pwsh -File .\setup_server_watchdog.ps1 -Action Uninstall" -f $colors.header
Write-Host ""

if ($Action -eq "Install") {
    OK "伺服器監控守護程式已設定！系統將自動監控伺服器並在離線時喚醒"
}
