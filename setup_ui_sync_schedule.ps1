#!/usr/bin/env pwsh
<#
.SYNOPSIS
    設定 UI 檔案自動檢查與同步排程
.DESCRIPTION
    建立 Windows Task Scheduler 排程，每小時自動檢查並同步 UI 檔案
#>

param(
    [string]$ScriptPath = "$PSScriptRoot\auto_deploy_ui.ps1",
    [int]$IntervalMinutes = 60,
    [string]$TaskName = "WuchangUIAutoSync",
    [ValidateSet("Install", "Uninstall", "Status")]
    [string]$Action = "Install"
)

$colors = @{ ok = "Green"; warn = "Yellow"; err = "Red"; info = "Cyan"; header = "Magenta" }
function H($t) { Write-Host "`n$('═'*70)" -f $colors.header; Write-Host "  $t" -f $colors.header; Write-Host $('═'*70) -f $colors.header }
function OK($m) { Write-Host "  [OK]   $m" -f $colors.ok }
function WW($m) { Write-Host "  [WARN] $m" -f $colors.warn }
function EE($m) { Write-Host "  [ERR]  $m" -f $colors.err }
function II($m) { Write-Host "  [INFO] $m" -f $colors.info }

H "UI 檔案自動同步排程管理"

# 檢查管理員權限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    EE "需要系統管理員權限"
    II "請以系統管理員身分執行 PowerShell"
    exit 1
}

switch ($Action) {
    "Status" {
        H "檢查排程狀態"
        
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($task) {
            OK "排程已存在"
            Write-Host ""
            Write-Host "  任務名稱: $($task.TaskName)" -f $colors.info
            Write-Host "  狀態: $($task.State)" -f $colors.info
            Write-Host "  描述: $($task.Description)" -f $colors.info
            
            $trigger = $task.Triggers[0]
            Write-Host "  觸發器: 每 $IntervalMinutes 分鐘" -f $colors.info
            
            $action = $task.Actions[0]
            Write-Host "  執行: $($action.Execute) $($action.Arguments)" -f $colors.info
            
            # 顯示最後執行時間
            $info = Get-ScheduledTaskInfo -TaskName $TaskName -ErrorAction SilentlyContinue
            if ($info) {
                Write-Host ""
                Write-Host "  最後執行: $($info.LastRunTime)" -f $colors.info
                Write-Host "  最後結果: $($info.LastTaskResult)" -f $colors.info
                Write-Host "  下次執行: $($info.NextRunTime)" -f $colors.info
            }
        } else {
            WW "排程不存在"
            II "使用 -Action Install 安裝排程"
        }
    }
    
    "Uninstall" {
        H "移除排程"
        
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($task) {
            try {
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
        H "安裝排程"
        
        # 檢查腳本是否存在
        if (-not (Test-Path $ScriptPath)) {
            EE "找不到腳本: $ScriptPath"
            exit 1
        }
        OK "腳本路徑: $ScriptPath"
        
        # 移除舊排程（如果存在）
        $existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($existing) {
            WW "發現舊排程，將先移除"
            Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        }
        
        # 建立排程動作
        $pwshPath = (Get-Command pwsh -ErrorAction SilentlyContinue).Source
        if (-not $pwshPath) {
            $pwshPath = "powershell.exe"
            WW "找不到 pwsh，使用 powershell.exe"
        }
        
        $arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""
        $action = New-ScheduledTaskAction -Execute $pwshPath -Argument $arguments
        
        # 建立觸發器（每小時）
        $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) -RepetitionDuration ([TimeSpan]::MaxValue)
        
        # 建立設定
        $settings = New-ScheduledTaskSettingsSet `
            -AllowStartIfOnBatteries `
            -DontStopIfGoingOnBatteries `
            -StartWhenAvailable `
            -RunOnlyIfNetworkAvailable `
            -ExecutionTimeLimit (New-TimeSpan -Minutes 30)
        
        # 建立主體（使用當前用戶）
        $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
        
        # 註冊排程
        try {
            Register-ScheduledTask `
                -TaskName $TaskName `
                -Action $action `
                -Trigger $trigger `
                -Settings $settings `
                -Principal $principal `
                -Description "五常 AI 系統 - UI 檔案自動檢查與同步 (每 $IntervalMinutes 分鐘)" `
                -ErrorAction Stop | Out-Null
            
            OK "排程已建立"
            Write-Host ""
            Write-Host "  任務名稱: $TaskName" -f $colors.info
            Write-Host "  執行頻率: 每 $IntervalMinutes 分鐘" -f $colors.info
            Write-Host "  執行腳本: $ScriptPath" -f $colors.info
            Write-Host "  執行帳戶: $env:USERNAME" -f $colors.info
            
        } catch {
            EE "建立排程失敗: $_"
            exit 1
        }
        
        # 立即執行一次測試
        H "測試執行"
        $confirm = Read-Host "是否立即執行一次測試? (y/N)"
        if ($confirm -eq "y" -or $confirm -eq "Y") {
            II "啟動測試執行..."
            Start-ScheduledTask -TaskName $TaskName
            OK "測試已啟動，請檢查日誌檔案"
            II "日誌: $PSScriptRoot\auto_deploy_ui.log"
        }
    }
}

# 管理建議
H "管理指令"
Write-Host ""
Write-Host "  查看狀態:" -f $colors.info
Write-Host "    pwsh -File .\setup_ui_sync_schedule.ps1 -Action Status" -f $colors.header
Write-Host ""
Write-Host "  手動執行一次:" -f $colors.info
Write-Host "    Start-ScheduledTask -TaskName '$TaskName'" -f $colors.header
Write-Host ""
Write-Host "  查看日誌:" -f $colors.info
Write-Host "    Get-Content '$PSScriptRoot\auto_deploy_ui.log' -Tail 50" -f $colors.header
Write-Host ""
Write-Host "  停用排程:" -f $colors.info
Write-Host "    Disable-ScheduledTask -TaskName '$TaskName'" -f $colors.header
Write-Host ""
Write-Host "  啟用排程:" -f $colors.info
Write-Host "    Enable-ScheduledTask -TaskName '$TaskName'" -f $colors.header
Write-Host ""
Write-Host "  移除排程:" -f $colors.info
Write-Host "    pwsh -File .\setup_ui_sync_schedule.ps1 -Action Uninstall" -f $colors.header
Write-Host ""

if ($Action -eq "Install") {
    OK "排程設定完成！系統將每 $IntervalMinutes 分鐘自動檢查並同步 UI 檔案"
}
