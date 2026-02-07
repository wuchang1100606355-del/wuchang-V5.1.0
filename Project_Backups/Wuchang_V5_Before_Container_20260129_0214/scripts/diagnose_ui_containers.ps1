# UI 容器錯誤排查腳本
# 診斷 UI 介面無回應問題

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "UI 容器錯誤排查" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 檢查 Docker 是否運行
Write-Host "`n[1/8] 檢查 Docker 服務狀態..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "✓ Docker 已安裝: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker 未安裝或未運行" -ForegroundColor Red
    exit 1
}

# 檢查 Docker 容器狀態
Write-Host "`n[2/8] 檢查容器狀態..." -ForegroundColor Yellow
try {
    $containers = docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>&1
    Write-Host $containers
} catch {
    Write-Host "⚠ 無法取得容器列表" -ForegroundColor Yellow
}

# 檢查特定 UI 相關容器
Write-Host "`n[3/8] 檢查 UI 相關容器..." -ForegroundColor Yellow
$uiContainers = @("wuchang-web", "wuchang-ai", "wuchang-status", "uptime-kuma", "portainer")

foreach ($container in $uiContainers) {
    try {
        $status = docker ps -a --filter "name=$container" --format "{{.Status}}" 2>&1
        if ($status -and $status -notmatch "error") {
            $color = if ($status -match "Up") { "Green" } else { "Red" }
            Write-Host "  $container : $status" -ForegroundColor $color
            
            # 檢查端口映射
            $ports = docker port $container 2>&1
            if ($ports -and $ports -notmatch "error") {
                Write-Host "    端口: $ports" -ForegroundColor Gray
            }
        } else {
            Write-Host "  $container : 未找到" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  $container : 檢查失敗" -ForegroundColor Yellow
    }
}

# 檢查容器日誌
Write-Host "`n[4/8] 檢查容器日誌（最近 20 行）..." -ForegroundColor Yellow
foreach ($container in $uiContainers) {
    try {
        $exists = docker ps -a --filter "name=$container" --format "{{.Names}}" 2>&1
        if ($exists -and $exists -notmatch "error") {
            Write-Host "`n--- $container 日誌 ---" -ForegroundColor Cyan
            docker logs --tail 20 $container 2>&1 | Select-Object -Last 10
        }
    } catch {
        Write-Host "  $container : 無法讀取日誌" -ForegroundColor Yellow
    }
}

# 檢查端口占用
Write-Host "`n[5/8] 檢查 UI 端口占用..." -ForegroundColor Yellow
$ports = @(8069, 8080, 3001, 8888, 9000)
foreach ($port in $ports) {
    try {
        $process = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        if ($process) {
            $procInfo = Get-Process -Id $process.OwningProcess -ErrorAction SilentlyContinue
            $procName = if ($procInfo) { $procInfo.ProcessName } else { "Unknown" }
            Write-Host "  端口 $port : 被占用 (PID: $($process.OwningProcess), 程序: $procName)" -ForegroundColor Yellow
        } else {
            Write-Host "  端口 $port : 可用" -ForegroundColor Green
        }
    } catch {
        Write-Host "  端口 $port : 檢查失敗" -ForegroundColor Yellow
    }
}

# 檢查容器資源使用
Write-Host "`n[6/8] 檢查容器資源使用..." -ForegroundColor Yellow
try {
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" 2>&1 | Select-Object -First 10
} catch {
    Write-Host "⚠ 無法取得資源使用資訊" -ForegroundColor Yellow
}

# 檢查網路連接
Write-Host "`n[7/8] 檢查網路連接..." -ForegroundColor Yellow
$endpoints = @(
    @{Name="Odoo"; URL="http://localhost:8069/web/health"},
    @{Name="AI Assistant"; URL="http://localhost:8080/health"},
    @{Name="Status Dashboard"; URL="http://localhost:3001/health"},
    @{Name="AI Supervisor"; URL="http://localhost:8888/api/supervisor/status"},
    @{Name="Portainer"; URL="http://localhost:9000"}
)

foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri $endpoint.URL -Method Get -TimeoutSec 3 -ErrorAction Stop
        Write-Host "  $($endpoint.Name) : ✓ 可訪問 (狀態碼: $($response.StatusCode))" -ForegroundColor Green
    } catch {
        Write-Host "  $($endpoint.Name) : ✗ 無法訪問" -ForegroundColor Red
    }
}

# 檢查 Docker Compose 狀態
Write-Host "`n[8/8] 檢查 Docker Compose 狀態..." -ForegroundColor Yellow
if (Test-Path "docker-compose.yml") {
    Write-Host "✓ docker-compose.yml 存在" -ForegroundColor Green
    
    # 檢查服務狀態
    try {
        docker-compose ps 2>&1 | Select-Object -First 20
    } catch {
        Write-Host "⚠ 無法執行 docker-compose ps" -ForegroundColor Yellow
    }
} else {
    Write-Host "✗ docker-compose.yml 不存在" -ForegroundColor Red
}

# 生成診斷報告
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "診斷完成" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n建議操作:" -ForegroundColor Yellow
Write-Host "1. 如果容器未運行，執行: docker-compose up -d" -ForegroundColor White
Write-Host "2. 如果端口被占用，檢查並停止占用端口的程序" -ForegroundColor White
Write-Host "3. 查看完整日誌: docker-compose logs -f" -ForegroundColor White
Write-Host "4. 重啟服務: docker-compose restart" -ForegroundColor White
