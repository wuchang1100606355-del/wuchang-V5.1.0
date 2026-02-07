# 系統更新腳本
# 功能：更新 Docker 映像檔、重新啟動容器、檢查系統狀態

function Log-Message {
    param (
        [string]$Message,
        [string]$Level = "INFO"
    )
    $icons = @{
        "INFO" = "ℹ️"
        "OK" = "✅"
        "WARN" = "⚠️"
        "ERROR" = "❌"
        "PROGRESS" = "🔄"
    }
    $icon = $icons.($Level)
    Write-Host "$icon [$Level] $Message"
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "系統更新工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 步驟 1: 拉取最新 Docker 映像檔
Log-Message "步驟 1: 更新 Docker 映像檔..." "PROGRESS"

$images = @(
    "odoo:17.0",
    "postgres:15",
    "caddy:2",
    "cloudflare/cloudflared:latest",
    "ollama/ollama:latest",
    "portainer/portainer-ce:latest",
    "louislam/uptime-kuma:latest"
)

$updatedImages = @()
foreach ($image in $images) {
    Log-Message "正在拉取 $image..." "INFO"
    try {
        docker pull $image 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Log-Message "✓ $image 更新成功" "OK"
            $updatedImages += $image
        } else {
            Log-Message "✗ $image 更新失敗" "WARN"
        }
    } catch {
        Log-Message "✗ $image 更新時發生錯誤: $($_.Exception.Message)" "ERROR"
    }
}

Write-Host ""
Log-Message "已更新 $($updatedImages.Count) 個映像檔" "INFO"

# 步驟 2: 重新建立並啟動容器
Write-Host ""
Log-Message "步驟 2: 重新啟動容器..." "PROGRESS"

$composeFile = "docker-compose.unified.yml"
if (Test-Path $composeFile) {
    try {
        Log-Message "使用 docker-compose 重新建立容器..." "INFO"
        docker-compose -f $composeFile --profile system --profile ui up -d --force-recreate 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Log-Message "✓ 容器重新建立成功" "OK"
        } else {
            Log-Message "✗ 容器重新建立失敗" "ERROR"
        }
    } catch {
        Log-Message "✗ 重新建立容器時發生錯誤: $($_.Exception.Message)" "ERROR"
    }
} else {
    Log-Message "未找到 docker-compose.unified.yml" "WARN"
}

# 步驟 3: 檢查容器狀態
Write-Host ""
Log-Message "步驟 3: 檢查容器狀態..." "PROGRESS"
Start-Sleep -Seconds 10  # 等待容器啟動

try {
    $containers = docker ps --format "{{.Names}}\t{{.Status}}" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Log-Message "運行中的容器：" "INFO"
        $containers | ForEach-Object {
            if ($_ -match "^(\S+)\s+(.+)$") {
                $name = $matches[1]
                $status = $matches[2]
                if ($status -match "Up") {
                    Write-Host "  ✅ $name - $status" -ForegroundColor Green
                } else {
                    Write-Host "  ⏸️ $name - $status" -ForegroundColor Yellow
                }
            }
        }
    }
} catch {
    Log-Message "檢查容器狀態時發生錯誤" "WARN"
}

# 步驟 4: 檢查系統健康度
Write-Host ""
Log-Message "步驟 4: 檢查系統健康度..." "PROGRESS"

try {
    $runningContainers = (docker ps --format "{{.Names}}" | Measure-Object).Count
    $totalContainers = (docker ps -a --format "{{.Names}}" | Measure-Object).Count
    
    Log-Message "容器狀態: $runningContainers/$totalContainers 運行中" "INFO"
    
    if ($runningContainers -gt 0) {
        Log-Message "✓ 系統更新完成" "OK"
    } else {
        Log-Message "⚠️ 沒有運行中的容器" "WARN"
    }
} catch {
    Log-Message "檢查系統健康度時發生錯誤" "WARN"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ 系統更新完成" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
