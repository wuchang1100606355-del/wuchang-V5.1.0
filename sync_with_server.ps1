#!/usr/bin/env pwsh
<#
.SYNOPSIS
    雙向同步監視器 - 保持本機與伺服器文件同步
.PARAMETER Mode
    sync 模式: push (推送到伺服器), pull (拉取從伺服器), watch (連續監視)
#>

param(
    [ValidateSet('push', 'pull', 'watch', 'config')]
    [string]$Mode = 'watch'
)

# 配置
$config = @{
    ServerIP = "192.168.50.249"
    ServerUser = "admin"
    LocalPath = "C:\wuchang V5.1.0"
    RemotePath = "/home/admin"
    SyncDirs = @(
        "wuchang_os\addons",
        "wuchang_os\config",
        "config",
        "scripts",
        "memory_store",
        "downloads"
    )
    SyncInterval = 300  # 5 minutes
}

$ErrorActionPreference = "Continue"

function Write-Info {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ✓ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ✗ $Message" -ForegroundColor Red
}

function Sync-ToServer {
    Write-Info "開始同步至伺服器..."
    
    foreach ($dir in $config.SyncDirs) {
        $localDir = Join-Path $config.LocalPath $dir
        $remoteDir = "$($config.RemotePath)/$($dir -replace '\\', '/')"
        
        if (Test-Path $localDir) {
            Write-Info "同步: $dir"
            
            try {
                # 使用rsync通過SSH
                rsync -avz --delete `
                    "$localDir/" `
                    "$($config.ServerUser)@$($config.ServerIP):$remoteDir/"
                
                Write-Success "已同步: $dir"
            } catch {
                Write-Error "同步失敗 [$dir]: $_"
            }
        }
    }
    
    Write-Success "推送同步完成"
}

function Sync-FromServer {
    Write-Info "開始從伺服器拉取..."
    
    foreach ($dir in $config.SyncDirs) {
        $localDir = Join-Path $config.LocalPath $dir
        $remoteDir = "$($config.RemotePath)/$($dir -replace '\\', '/')"
        
        Write-Info "拉取: $dir"
        
        try {
            # 使用rsync通過SSH
            rsync -avz --delete `
                "$($config.ServerUser)@$($config.ServerIP):$remoteDir/" `
                "$localDir/"
            
            Write-Success "已拉取: $dir"
        } catch {
            Write-Error "拉取失敗 [$dir]: $_"
        }
    }
    
    Write-Success "拉取同步完成"
}

function Watch-Continuous {
    Write-Info "啟動連續監視模式..."
    Write-Info "同步間隔: $($config.SyncInterval) 秒"
    Write-Info "按 Ctrl+C 停止監視"
    
    $syncCount = 0
    
    while ($true) {
        $syncCount++
        Write-Info "第 $syncCount 次同步周期開始"
        
        # 先推送本地更改
        Sync-ToServer
        
        # 再拉取遠程更改
        Start-Sleep -Seconds 10
        Sync-FromServer
        
        Write-Info "等待 $($config.SyncInterval) 秒後進行下次同步..."
        Start-Sleep -Seconds $config.SyncInterval
    }
}

function Show-Config {
    Write-Host @"
┌─────────────────────────────────────────────────────┐
│        雙向同步配置信息                               │
├─────────────────────────────────────────────────────┤
│ 伺服器IP:      $($config.ServerIP)
│ 伺服器用戶:    $($config.ServerUser)
│ 本地路徑:      $($config.LocalPath)
│ 遠程路徑:      $($config.RemotePath)
│ 同步間隔:      $($config.SyncInterval) 秒
│
│ 同步目錄:
"@ 
    
    foreach ($dir in $config.SyncDirs) {
        Write-Host "│   • $dir"
    }
    
    Write-Host @"
│
│ 前置需求:
│   □ SSH密鑰配置完成
│   □ rsync已安裝
│   □ 網絡連接正常
│   □ 伺服器NFS/SMB已配置
└─────────────────────────────────────────────────────┘
"@
}

# 檢查前置條件
function Test-Prerequisites {
    Write-Info "檢查前置條件..."
    
    $checks = @{
        "SSH連接" = { ssh -o ConnectTimeout=5 "$($config.ServerUser)@$($config.ServerIP)" "echo OK" 2>&1 }
        "Rsync命令" = { rsync --version 2>&1 }
        "本地路徑" = { Test-Path $config.LocalPath }
    }
    
    foreach ($check in $checks.GetEnumerator()) {
        try {
            $result = & $check.Value
            if ($result) {
                Write-Success "$($check.Key): 正常"
            } else {
                Write-Error "$($check.Key): 失敗"
            }
        } catch {
            Write-Error "$($check.Key): $_"
        }
    }
}

# 主程序
Write-Host "`n═══════════════════════════════════════════════════════" -ForegroundColor Magenta
Write-Host "  五常AI系統 - 雙向同步監視器 v1.0" -ForegroundColor Magenta
Write-Host "═══════════════════════════════════════════════════════`n" -ForegroundColor Magenta

switch ($Mode) {
    "push" {
        Write-Info "推送模式: 將本地更改同步至伺服器"
        Sync-ToServer
    }
    "pull" {
        Write-Info "拉取模式: 將伺服器更改同步至本地"
        Sync-FromServer
    }
    "watch" {
        Test-Prerequisites
        Watch-Continuous
    }
    "config" {
        Show-Config
    }
}

Write-Host "`n" -ForegroundColor Cyan
