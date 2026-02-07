# 統一任務管理器
# 管理所有 Wuchang 系統相關的 Windows 定時任務
# 合規要求：符合 Google 非營利組織合規要求

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("list", "status", "install", "uninstall", "start", "stop", "enable", "disable", "health")]
    [string]$Action = "status",
    
    [Parameter(Mandatory=$false)]
    [string]$TaskName = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$All
)

$ErrorActionPreference = "Continue"
$Root = (Get-Location).Path

# 定義所有任務配置
$Tasks = @{
    "WuchangAutoComplianceCheck" = @{
        Description = "全自動合規和證書檢查 - 每小時執行"
        Script = "auto_compliance_certificate_check.py"
        Interval = "Hourly"
        Priority = "High"
        Required = $true
    }
    "WuchangHourlyDeploymentCheck" = @{
        Description = "每小時系統部署檢查"
        Script = "hourly_deployment_check.py"
        Interval = "Hourly"
        Priority = "High"
        Required = $true
    }
    "WuchangHealthMonitor" = @{
        Description = "系統健康監控 - 每 15 分鐘"
        Script = "wuchang_container_health.ps1"
        Interval = "15Minutes"
        Priority = "High"
        Required = $true
    }
    "DNSDailyCheck" = @{
        Description = "每日 DNS 檢查"
        Script = "dns_guard.ps1"
        Interval = "Daily"
        Priority = "Medium"
        Required = $false
    }
    "IntegrityDailyCheck" = @{
        Description = "每日完整性檢查"
        Script = "verify_integrity.ps1"
        Interval = "Daily"
        Priority = "Medium"
        Required = $false
    }
}

function Write-Log($msg) {
    $line = "[" + (Get-Date -Format "yyyy-MM-dd HH:mm:ss") + "] [TaskManager] " + $msg
    Write-Host $line
    try {
        $logFile = Join-Path $Root "logs\task_manager.log"
        $logDir = Split-Path -Parent $logFile
        if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
        Add-Content -Path $logFile -Value $line -Encoding UTF8
    } catch {}
}

function Get-TaskStatus($taskName) {
    try {
        $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        if ($task) {
            $info = Get-ScheduledTaskInfo -TaskName $taskName -ErrorAction SilentlyContinue
            return @{
                Exists = $true
                State = $task.State
                LastRunTime = $info.LastRunTime
                LastResult = $info.LastTaskResult
                NextRunTime = $info.NextRunTime
            }
        } else {
            return @{
                Exists = $false
                State = "NotInstalled"
            }
        }
    } catch {
        return @{
            Exists = $false
            State = "Error"
            Error = $_.Exception.Message
        }
    }
}

function Install-Task($taskName, $config) {
    Write-Log "安裝任務: $taskName"
    
    $scriptPath = Join-Path $Root "scripts\$($config.Script)"
    if (-not (Test-Path $scriptPath)) {
        Write-Log "  ❌ 腳本不存在: $scriptPath"
        return $false
    }
    
    # 檢查是否已存在
    $existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Log "  ⚠ 任務已存在，將更新..."
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    }
    
    # 確定執行方式
    if ($config.Script -like "*.py") {
        $executable = "python"
        $arguments = "`"$scriptPath`""
    } elseif ($config.Script -like "*.ps1") {
        $executable = "powershell.exe"
        $arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`""
    } else {
        Write-Log "  ❌ 不支持的腳本類型: $($config.Script)"
        return $false
    }
    
    # 創建動作
    $action = New-ScheduledTaskAction -Execute $executable -Argument $arguments -WorkingDirectory (Join-Path $Root "scripts")
    
    # 創建觸發器
    $trigger = switch ($config.Interval) {
        "Hourly" {
            New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(60) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 365)
        }
        "15Minutes" {
            New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(15) -RepetitionInterval (New-TimeSpan -Minutes 15) -RepetitionDuration (New-TimeSpan -Days 365)
        }
        "Daily" {
            New-ScheduledTaskTrigger -Daily -At "03:00"
        }
        default {
            New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(60) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 365)
        }
    }
    
    # 創建設置
    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -RunOnlyIfNetworkAvailable `
        -RestartCount 3 `
        -RestartInterval (New-TimeSpan -Minutes 1) `
        -ExecutionTimeLimit (New-TimeSpan -Hours 1)
    
    # 註冊任務
    try {
        Register-ScheduledTask `
            -TaskName $taskName `
            -Action $action `
            -Trigger $trigger `
            -Settings $settings `
            -Description $config.Description `
            -User $env:USERNAME `
            -RunLevel Highest | Out-Null
        
        Write-Log "  ✅ 任務已安裝: $taskName"
        return $true
    } catch {
        Write-Log "  ❌ 安裝失敗: $($_.Exception.Message)"
        return $false
    }
}

function Show-Status {
    Write-Host "`n" + "="*80
    Write-Host "  Wuchang 任務管理器 - 任務狀態"
    Write-Host "="*80
    Write-Host ""
    
    $allOk = $true
    foreach ($taskName in $Tasks.Keys) {
        $config = $Tasks[$taskName]
        $status = Get-TaskStatus $taskName
        
        $statusIcon = if ($status.Exists -and $status.State -eq "Ready") { "✅" } elseif ($status.Exists) { "⚠️" } else { "❌" }
        
        Write-Host "$statusIcon $taskName"
        Write-Host "   描述: $($config.Description)"
        Write-Host "   狀態: $($status.State)"
        
        if ($status.Exists) {
            if ($status.LastRunTime) {
                Write-Host "   最後執行: $($status.LastRunTime)"
            }
            if ($status.NextRunTime) {
                Write-Host "   下次執行: $($status.NextRunTime)"
            }
            if ($status.LastResult -and $status.LastResult -ne 0) {
                Write-Host "   最後結果: ❌ 失敗 (退出碼: $($status.LastResult))"
                $allOk = $false
            }
        } else {
            $allOk = $false
        }
        Write-Host ""
    }
    
    Write-Host "="*80
    if ($allOk) {
        Write-Host "  ✅ 所有任務狀態正常"
    } else {
        Write-Host "  ⚠️ 部分任務需要關注"
    }
    Write-Host ""
}

function Show-Health {
    Write-Host "`n" + "="*80
    Write-Host "  Wuchang 任務管理器 - 健康檢查"
    Write-Host "="*80
    Write-Host ""
    
    $health = @{
        Total = $Tasks.Count
        Installed = 0
        Running = 0
        Failed = 0
        Missing = 0
    }
    
    foreach ($taskName in $Tasks.Keys) {
        $status = Get-TaskStatus $taskName
        if ($status.Exists) {
            $health.Installed++
            if ($status.State -eq "Ready") {
                $health.Running++
            } elseif ($status.State -eq "Running") {
                $health.Running++
            } else {
                $health.Failed++
            }
        } else {
            $health.Missing++
        }
    }
    
    Write-Host "  總任務數: $($health.Total)"
    Write-Host "  已安裝: $($health.Installed)"
    Write-Host "  運行中: $($health.Running)"
    Write-Host "  失敗: $($health.Failed)"
    Write-Host "  缺失: $($health.Missing)"
    Write-Host ""
    
    $healthScore = [math]::Round(($health.Running / $health.Total) * 100, 1)
    Write-Host "  健康分數: $healthScore%"
    Write-Host ""
    
    if ($healthScore -ge 90) {
        Write-Host "  ✅ 系統健康狀態良好"
    } elseif ($healthScore -ge 70) {
        Write-Host "  ⚠️ 系統健康狀態一般，建議檢查"
    } else {
        Write-Host "  ❌ 系統健康狀態不佳，需要修復"
    }
    Write-Host ""
}

# 主邏輯
switch ($Action) {
    "list" {
        Write-Host "`n已定義的任務列表:"
        Write-Host "="*80
        foreach ($taskName in $Tasks.Keys) {
            $config = $Tasks[$taskName]
            Write-Host "  - $taskName"
            Write-Host "    描述: $($config.Description)"
            Write-Host "    間隔: $($config.Interval)"
            Write-Host "    優先級: $($config.Priority)"
            Write-Host "    必需: $(if ($config.Required) { '是' } else { '否' })"
            Write-Host ""
        }
    }
    
    "status" {
        if ($TaskName) {
            if ($Tasks.ContainsKey($TaskName)) {
                $status = Get-TaskStatus $TaskName
                Write-Host "`n任務狀態: $TaskName"
                Write-Host "="*80
                $status.PSObject.Properties | ForEach-Object {
                    Write-Host "  $($_.Name): $($_.Value)"
                }
            } else {
                Write-Host "❌ 未知任務: $TaskName"
            }
        } else {
            Show-Status
        }
    }
    
    "install" {
        $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
        if (-not $isAdmin) {
            Write-Host "❌ 需要管理員權限"
            Write-Host "請以管理員權限運行此腳本"
            exit 1
        }
        
        if ($TaskName) {
            if ($Tasks.ContainsKey($TaskName)) {
                Install-Task $TaskName $Tasks[$TaskName]
            } else {
                Write-Host "❌ 未知任務: $TaskName"
            }
        } elseif ($All) {
            Write-Host "`n安裝所有任務..."
            Write-Host "="*80
            foreach ($taskName in $Tasks.Keys) {
                Install-Task $taskName $Tasks[$taskName]
            }
        } else {
            Write-Host "請指定任務名稱或使用 -All 參數安裝所有任務"
            Write-Host "可用任務: $($Tasks.Keys -join ', ')"
        }
    }
    
    "uninstall" {
        $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
        if (-not $isAdmin) {
            Write-Host "❌ 需要管理員權限"
            exit 1
        }
        
        if ($TaskName) {
            try {
                Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
                Write-Log "任務已卸載: $TaskName"
                Write-Host "✅ 任務已卸載: $TaskName"
            } catch {
                Write-Host "❌ 卸載失敗: $($_.Exception.Message)"
            }
        } else {
            Write-Host "請指定任務名稱"
        }
    }
    
    "start" {
        if ($TaskName) {
            try {
                Start-ScheduledTask -TaskName $TaskName
                Write-Host "✅ 任務已啟動: $TaskName"
            } catch {
                Write-Host "❌ 啟動失敗: $($_.Exception.Message)"
            }
        } else {
            Write-Host "請指定任務名稱"
        }
    }
    
    "stop" {
        if ($TaskName) {
            try {
                Stop-ScheduledTask -TaskName $TaskName
                Write-Host "✅ 任務已停止: $TaskName"
            } catch {
                Write-Host "❌ 停止失敗: $($_.Exception.Message)"
            }
        } else {
            Write-Host "請指定任務名稱"
        }
    }
    
    "enable" {
        if ($TaskName) {
            try {
                Enable-ScheduledTask -TaskName $TaskName
                Write-Host "✅ 任務已啟用: $TaskName"
            } catch {
                Write-Host "❌ 啟用失敗: $($_.Exception.Message)"
            }
        } else {
            Write-Host "請指定任務名稱"
        }
    }
    
    "disable" {
        if ($TaskName) {
            try {
                Disable-ScheduledTask -TaskName $TaskName
                Write-Host "✅ 任務已禁用: $TaskName"
            } catch {
                Write-Host "❌ 禁用失敗: $($_.Exception.Message)"
            }
        } else {
            Write-Host "請指定任務名稱"
        }
    }
    
    "health" {
        Show-Health
    }
    
    default {
        Write-Host "用法: .\wuchang_task_manager.ps1 -Action <action> [-TaskName <name>] [-All]"
        Write-Host ""
        Write-Host "操作:"
        Write-Host "  list      - 列出所有定義的任務"
        Write-Host "  status    - 顯示任務狀態（默認）"
        Write-Host "  install   - 安裝任務"
        Write-Host "  uninstall - 卸載任務"
        Write-Host "  start     - 啟動任務"
        Write-Host "  stop      - 停止任務"
        Write-Host "  enable    - 啟用任務"
        Write-Host "  disable   - 禁用任務"
        Write-Host "  health    - 健康檢查"
        Write-Host ""
        Write-Host "示例:"
        Write-Host "  .\wuchang_task_manager.ps1 -Action status"
        Write-Host "  .\wuchang_task_manager.ps1 -Action install -All"
        Write-Host "  .\wuchang_task_manager.ps1 -Action start -TaskName WuchangAutoComplianceCheck"
    }
}

Write-Host ""
Write-Host "✅ 合規: 符合 Google 非營利組織合規要求" -ForegroundColor Green
