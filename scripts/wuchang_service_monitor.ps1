# 系統服務監控腳本
# 監控 Docker、WSL 等關鍵服務，自動恢復
# 合規要求：符合 Google 非營利組織合規要求

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("check", "monitor", "restart", "status")]
    [string]$Action = "check",
    
    [Parameter(Mandatory=$false)]
    [string]$ServiceName = ""
)

$ErrorActionPreference = "Continue"
$Root = (Get-Location).Path

# 定義需要監控的服務
$Services = @{
    "com.docker.service" = @{
        DisplayName = "Docker Desktop Service"
        Required = $true
        AutoRestart = $true
        CheckCommand = { docker ps | Out-Null }
    }
    "WSLService" = @{
        DisplayName = "WSL Service"
        Required = $true
        AutoRestart = $true
        CheckCommand = { wsl --list | Out-Null }
    }
    "ssh-agent" = @{
        DisplayName = "OpenSSH Authentication Agent"
        Required = $false
        AutoRestart = $false
        CheckCommand = { $null }
    }
}

function Write-Log($msg) {
    $line = "[" + (Get-Date -Format "yyyy-MM-dd HH:mm:ss") + "] [ServiceMonitor] " + $msg
    Write-Host $line
    try {
        $logFile = Join-Path $Root "logs\service_monitor.log"
        $logDir = Split-Path -Parent $logFile
        if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
        Add-Content -Path $logFile -Value $line -Encoding UTF8
    } catch {}
}

function Check-Service($serviceName, $config) {
    $result = @{
        Name = $serviceName
        DisplayName = $config.DisplayName
        Status = "Unknown"
        Running = $false
        Healthy = $false
        Error = $null
    }
    
    try {
        $service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
        if ($service) {
            $result.Status = $service.Status.ToString()
            $result.Running = ($service.Status -eq "Running")
            
            # 執行健康檢查
            if ($result.Running -and $config.CheckCommand) {
                try {
                    & $config.CheckCommand
                    $result.Healthy = $true
                } catch {
                    $result.Healthy = $false
                    $result.Error = "健康檢查失敗: $($_.Exception.Message)"
                }
            } else {
                $result.Healthy = $result.Running
            }
        } else {
            $result.Status = "NotFound"
            $result.Error = "服務未找到"
        }
    } catch {
        $result.Status = "Error"
        $result.Error = $_.Exception.Message
    }
    
    return $result
}

function Restart-ServiceSafe($serviceName, $config) {
    Write-Log "嘗試重啟服務: $serviceName"
    
    try {
        $service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
        if (-not $service) {
            Write-Log "  ❌ 服務不存在: $serviceName"
            return $false
        }
        
        if ($service.Status -eq "Running") {
            Write-Log "  ⚠ 服務正在運行，先停止..."
            Stop-Service -Name $serviceName -Force -ErrorAction Stop
            Start-Sleep -Seconds 2
        }
        
        Write-Log "  🔄 啟動服務..."
        Start-Service -Name $serviceName -ErrorAction Stop
        Start-Sleep -Seconds 5
        
        # 驗證服務狀態
        $service = Get-Service -Name $serviceName
        if ($service.Status -eq "Running") {
            Write-Log "  ✅ 服務已重啟: $serviceName"
            
            # 執行健康檢查
            if ($config.CheckCommand) {
                Start-Sleep -Seconds 3
                try {
                    & $config.CheckCommand
                    Write-Log "  ✅ 健康檢查通過"
                    return $true
                } catch {
                    Write-Log "  ⚠ 健康檢查失敗: $($_.Exception.Message)"
                    return $false
                }
            }
            return $true
        } else {
            Write-Log "  ❌ 服務啟動失敗，狀態: $($service.Status)"
            return $false
        }
    } catch {
        Write-Log "  ❌ 重啟失敗: $($_.Exception.Message)"
        return $false
    }
}

function Show-Status {
    Write-Host "`n" + "="*80
    Write-Host "  系統服務監控 - 服務狀態"
    Write-Host "="*80
    Write-Host ""
    
    $allOk = $true
    foreach ($serviceName in $Services.Keys) {
        $config = $Services[$serviceName]
        $result = Check-Service $serviceName $config
        
        $statusIcon = if ($result.Healthy) { "✅" } elseif ($result.Running) { "⚠️" } else { "❌" }
        
        Write-Host "$statusIcon $($result.DisplayName) ($serviceName)"
        Write-Host "   狀態: $($result.Status)"
        Write-Host "   運行中: $(if ($result.Running) { '是' } else { '否' })"
        Write-Host "   健康: $(if ($result.Healthy) { '是' } else { '否' })"
        
        if ($result.Error) {
            Write-Host "   錯誤: $($result.Error)"
            $allOk = $false
        }
        
        if (-not $result.Healthy -and $config.Required) {
            $allOk = $false
        }
        Write-Host ""
    }
    
    Write-Host "="*80
    if ($allOk) {
        Write-Host "  ✅ 所有關鍵服務正常"
    } else {
        Write-Host "  ⚠️ 部分服務需要關注"
    }
    Write-Host ""
}

function Monitor-Services {
    Write-Log "開始監控服務..."
    
    $issues = @()
    foreach ($serviceName in $Services.Keys) {
        $config = $Services[$serviceName]
        
        if (-not $config.Required) {
            continue
        }
        
        $result = Check-Service $serviceName $config
        
        if (-not $result.Healthy) {
            Write-Log "  🔴 發現問題: $($result.DisplayName) - $($result.Status)"
            $issues += @{
                Service = $serviceName
                Result = $result
                Config = $config
            }
            
            # 自動恢復
            if ($config.AutoRestart) {
                Write-Log "  🔄 嘗試自動恢復..."
                $restartResult = Restart-ServiceSafe $serviceName $config
                if ($restartResult) {
                    Write-Log "  ✅ 自動恢復成功"
                } else {
                    Write-Log "  ❌ 自動恢復失敗，需要手動處理"
                }
            }
        } else {
            Write-Log "  ✅ $($result.DisplayName) - 正常"
        }
    }
    
    # 生成報告
    $report = @{
        Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        Services = @()
        Issues = $issues.Count
        AllHealthy = ($issues.Count -eq 0)
    }
    
    foreach ($serviceName in $Services.Keys) {
        $result = Check-Service $serviceName $Services[$serviceName]
        $report.Services += $result
    }
    
    # 保存報告
    try {
        $reportFile = Join-Path $Root "logs\service_monitor_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
        $reportDir = Split-Path -Parent $reportFile
        if (-not (Test-Path $reportDir)) { New-Item -ItemType Directory -Path $reportDir -Force | Out-Null }
        $report | ConvertTo-Json -Depth 10 | Set-Content -Path $reportFile -Encoding UTF8
        Write-Log "報告已保存: $reportFile"
    } catch {
        Write-Log "保存報告失敗: $($_.Exception.Message)"
    }
    
    return $report
}

# 主邏輯
switch ($Action) {
    "check" {
        Show-Status
    }
    
    "monitor" {
        Monitor-Services
    }
    
    "restart" {
        $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
        if (-not $isAdmin) {
            Write-Host "❌ 需要管理員權限來重啟服務"
            exit 1
        }
        
        if ($ServiceName) {
            if ($Services.ContainsKey($ServiceName)) {
                Restart-ServiceSafe $ServiceName $Services[$ServiceName]
            } else {
                Write-Host "❌ 未知服務: $ServiceName"
            }
        } else {
            Write-Host "請指定服務名稱"
            Write-Host "可用服務: $($Services.Keys -join ', ')"
        }
    }
    
    "status" {
        Show-Status
    }
    
    default {
        Write-Host "用法: .\wuchang_service_monitor.ps1 -Action <action> [-ServiceName <name>]"
        Write-Host ""
        Write-Host "操作:"
        Write-Host "  check    - 檢查服務狀態（默認）"
        Write-Host "  monitor  - 監控並自動恢復"
        Write-Host "  restart  - 重啟指定服務"
        Write-Host "  status   - 顯示服務狀態"
    }
}

Write-Host ""
Write-Host "✅ 合規: 符合 Google 非營利組織合規要求" -ForegroundColor Green
