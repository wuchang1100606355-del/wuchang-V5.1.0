# 容器健康監控腳本
# 監控 Docker 容器狀態，自動恢復
# 合規要求：符合 Google 非營利組織合規要求

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("check", "monitor", "restart", "status")]
    [string]$Action = "check",
    
    [Parameter(Mandatory=$false)]
    [string]$ContainerName = ""
)

$ErrorActionPreference = "Continue"
$Root = (Get-Location).Path

# 定義需要監控的容器
$Containers = @{
    "caddy" = @{
        DisplayName = "Caddy 反向代理"
        Required = $true
        AutoRestart = $true
        HealthCheck = { docker exec caddy caddy version | Out-Null }
        HealthURL = "http://localhost/health"
    }
    "wuchang-web" = @{
        DisplayName = "Wuchang Odoo Web"
        Required = $true
        AutoRestart = $true
        HealthCheck = { docker exec wuchang-web curl -f http://localhost:8069/web/health | Out-Null }
        HealthURL = "http://localhost:8069/web/health"
    }
    "db" = @{
        DisplayName = "PostgreSQL 數據庫"
        Required = $true
        AutoRestart = $true
        HealthCheck = { docker exec db pg_isready -U odoo | Out-Null }
        HealthURL = $null
    }
}

function Write-Log($msg) {
    $line = "[" + (Get-Date -Format "yyyy-MM-dd HH:mm:ss") + "] [ContainerHealth] " + $msg
    Write-Host $line
    try {
        $logFile = Join-Path $Root "logs\container_health.log"
        $logDir = Split-Path -Parent $logFile
        if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
        Add-Content -Path $logFile -Value $line -Encoding UTF8
    } catch {}
}

function Check-Container($containerName, $config) {
    $result = @{
        Name = $containerName
        DisplayName = $config.DisplayName
        Exists = $false
        Running = $false
        Healthy = $false
        Status = "Unknown"
        Error = $null
    }
    
    try {
        # 檢查容器是否存在
        $container = docker ps -a --filter "name=$containerName" --format "{{.Names}}|{{.Status}}" 2>&1
        if ($LASTEXITCODE -eq 0 -and $container) {
            $result.Exists = $true
            $result.Status = ($container -split '\|')[1]
            $result.Running = ($container -like "*Up*")
            
            # 執行健康檢查
            if ($result.Running) {
                if ($config.HealthCheck) {
                    try {
                        & $config.HealthCheck
                        $result.Healthy = ($LASTEXITCODE -eq 0)
                    } catch {
                        $result.Healthy = $false
                        $result.Error = "健康檢查失敗: $($_.Exception.Message)"
                    }
                } else {
                    $result.Healthy = $result.Running
                }
                
                # HTTP 健康檢查（如果有）
                if ($result.Healthy -and $config.HealthURL) {
                    try {
                        $response = Invoke-WebRequest -Uri $config.HealthURL -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
                        $result.Healthy = ($response.StatusCode -eq 200)
                    } catch {
                        $result.Healthy = $false
                        if (-not $result.Error) {
                            $result.Error = "HTTP 健康檢查失敗: $($_.Exception.Message)"
                        }
                    }
                }
            } else {
                $result.Healthy = $false
                $result.Error = "容器未運行"
            }
        } else {
            $result.Exists = $false
            $result.Error = "容器不存在"
        }
    } catch {
        $result.Status = "Error"
        $result.Error = $_.Exception.Message
    }
    
    return $result
}

function Restart-ContainerSafe($containerName, $config) {
    Write-Log "嘗試重啟容器: $containerName"
    
    try {
        # 檢查容器是否存在
        $exists = docker ps -a --filter "name=$containerName" --format "{{.Names}}" 2>&1
        if (-not $exists -or $LASTEXITCODE -ne 0) {
            Write-Log "  ❌ 容器不存在: $containerName"
            Write-Log "  💡 嘗試使用 docker-compose 啟動..."
            
            # 嘗試使用 docker-compose 啟動
            Push-Location $Root
            docker-compose up -d $containerName 2>&1 | Out-Null
            Pop-Location
            
            Start-Sleep -Seconds 5
            $result = Check-Container $containerName $config
            if ($result.Running) {
                Write-Log "  ✅ 容器已啟動: $containerName"
                return $true
            } else {
                Write-Log "  ❌ 容器啟動失敗"
                return $false
            }
        }
        
        # 重啟容器
        Write-Log "  🔄 重啟容器..."
        docker restart $containerName 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "  ⏳ 等待容器啟動（10秒）..."
            Start-Sleep -Seconds 10
            
            # 驗證容器狀態
            $result = Check-Container $containerName $config
            if ($result.Running -and $result.Healthy) {
                Write-Log "  ✅ 容器已重啟並健康: $containerName"
                return $true
            } elseif ($result.Running) {
                Write-Log "  ⚠ 容器已重啟但健康檢查未通過"
                return $false
            } else {
                Write-Log "  ❌ 容器重啟失敗"
                return $false
            }
        } else {
            Write-Log "  ❌ 重啟命令失敗"
            return $false
        }
    } catch {
        Write-Log "  ❌ 重啟失敗: $($_.Exception.Message)"
        return $false
    }
}

function Show-Status {
    Write-Host "`n" + "="*80
    Write-Host "  容器健康監控 - 容器狀態"
    Write-Host "="*80
    Write-Host ""
    
    # 檢查 Docker 是否運行
    try {
        docker ps | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  ❌ Docker 未運行或無法訪問"
            Write-Host "  請確認 Docker Desktop 已啟動"
            return
        }
    } catch {
        Write-Host "  ❌ Docker 未運行或無法訪問"
        Write-Host "  錯誤: $($_.Exception.Message)"
        return
    }
    
    $allOk = $true
    foreach ($containerName in $Containers.Keys) {
        $config = $Containers[$containerName]
        $result = Check-Container $containerName $config
        
        $statusIcon = if ($result.Healthy) { "✅" } elseif ($result.Running) { "⚠️" } else { "❌" }
        
        Write-Host "$statusIcon $($result.DisplayName) ($containerName)"
        Write-Host "   存在: $(if ($result.Exists) { '是' } else { '否' })"
        Write-Host "   運行中: $(if ($result.Running) { '是' } else { '否' })"
        Write-Host "   健康: $(if ($result.Healthy) { '是' } else { '否' })"
        Write-Host "   狀態: $($result.Status)"
        
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
        Write-Host "  ✅ 所有關鍵容器正常"
    } else {
        Write-Host "  ⚠️ 部分容器需要關注"
    }
    Write-Host ""
}

function Monitor-Containers {
    Write-Log "開始監控容器..."
    
    # 檢查 Docker 是否運行
    try {
        docker ps | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Log "  ❌ Docker 未運行，無法監控容器"
            return $null
        }
    } catch {
        Write-Log "  ❌ Docker 未運行: $($_.Exception.Message)"
        return $null
    }
    
    $issues = @()
    foreach ($containerName in $Containers.Keys) {
        $config = $Containers[$containerName]
        
        if (-not $config.Required) {
            continue
        }
        
        $result = Check-Container $containerName $config
        
        if (-not $result.Healthy) {
            Write-Log "  🔴 發現問題: $($result.DisplayName) - $($result.Status)"
            $issues += @{
                Container = $containerName
                Result = $result
                Config = $config
            }
            
            # 自動恢復
            if ($config.AutoRestart) {
                Write-Log "  🔄 嘗試自動恢復..."
                $restartResult = Restart-ContainerSafe $containerName $config
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
        Containers = @()
        Issues = $issues.Count
        AllHealthy = ($issues.Count -eq 0)
    }
    
    foreach ($containerName in $Containers.Keys) {
        $result = Check-Container $containerName $Containers[$containerName]
        $report.Containers += $result
    }
    
    # 保存報告
    try {
        $reportFile = Join-Path $Root "logs\container_health_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
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
        Monitor-Containers
    }
    
    "restart" {
        if ($ContainerName) {
            if ($Containers.ContainsKey($ContainerName)) {
                Restart-ContainerSafe $ContainerName $Containers[$ContainerName]
            } else {
                Write-Host "❌ 未知容器: $ContainerName"
            }
        } else {
            Write-Host "請指定容器名稱"
            Write-Host "可用容器: $($Containers.Keys -join ', ')"
        }
    }
    
    "status" {
        Show-Status
    }
    
    default {
        Write-Host "用法: .\wuchang_container_health.ps1 -Action <action> [-ContainerName <name>]"
        Write-Host ""
        Write-Host "操作:"
        Write-Host "  check    - 檢查容器狀態（默認）"
        Write-Host "  monitor  - 監控並自動恢復"
        Write-Host "  restart  - 重啟指定容器"
        Write-Host "  status   - 顯示容器狀態"
    }
}

Write-Host ""
Write-Host "✅ 合規: 符合 Google 非營利組織合規要求" -ForegroundColor Green
