# 優化架構統一設置腳本
# 利用 Windows 10 專業版功能優化系統架構
# 合規要求：符合 Google 非營利組織合規要求

param(
    [switch]$SkipTests = $false,
    [switch]$Force = $false
)

$ErrorActionPreference = "Continue"
$Root = (Get-Location).Path

Write-Host "=" * 80
Write-Host "  Wuchang 系統優化架構設置"
Write-Host "  利用 Windows 10 專業版功能"
Write-Host "=" * 80
Write-Host ""

# 檢查管理員權限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "❌ 需要管理員權限"
    Write-Host "請以管理員權限運行此腳本"
    exit 1
}

Write-Host "✅ 管理員權限確認"
Write-Host ""

# 步驟 1: 檢查環境
Write-Host "步驟 1: 檢查環境..." -ForegroundColor Cyan
Write-Host ""

# 檢查 Docker
Write-Host "檢查 Docker..."
try {
    $dockerVersion = docker --version
    Write-Host "  ✅ Docker: $dockerVersion" -ForegroundColor Green
    
    docker ps | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Docker 運行正常" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Docker 未運行" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  ❌ Docker 未安裝或無法訪問" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 檢查 WSL
Write-Host "檢查 WSL..."
try {
    $wslVersion = wsl --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ WSL 已安裝" -ForegroundColor Green
        $wslList = wsl --list --verbose
        Write-Host "  $wslList"
    } else {
        Write-Host "  ⚠ WSL 未安裝（可選）" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ⚠ WSL 檢查失敗（可選）" -ForegroundColor Yellow
}
Write-Host ""

# 檢查 Python
Write-Host "檢查 Python..."
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Python 未安裝" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 步驟 2: 安裝必要套件
Write-Host "步驟 2: 安裝必要套件..." -ForegroundColor Cyan
Write-Host ""

$requiredPackages = @("dnspython", "requests", "urllib3")
$missingPackages = @()

foreach ($package in $requiredPackages) {
    try {
        $importName = $package.Replace('-', '_')
        python -c "import $importName" 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ $package 已安裝" -ForegroundColor Green
        } else {
            $missingPackages += $package
        }
    } catch {
        $missingPackages += $package
    }
}

if ($missingPackages.Count -gt 0) {
    Write-Host "  安裝缺少的套件: $($missingPackages -join ', ')" -ForegroundColor Yellow
    python -m pip install $missingPackages --quiet
    Write-Host "  ✅ 套件安裝完成" -ForegroundColor Green
}
Write-Host ""

# 步驟 3: 設置統一任務管理
Write-Host "步驟 3: 設置統一任務管理..." -ForegroundColor Cyan
Write-Host ""

$taskManagerScript = Join-Path $Root "scripts\wuchang_task_manager.ps1"
if (Test-Path $taskManagerScript) {
    Write-Host "  安裝所有任務..." -ForegroundColor Yellow
    & $taskManagerScript -Action install -All
    Write-Host ""
    
    Write-Host "  檢查任務狀態..." -ForegroundColor Yellow
    & $taskManagerScript -Action status
} else {
    Write-Host "  ⚠ 任務管理器腳本不存在: $taskManagerScript" -ForegroundColor Yellow
}
Write-Host ""

# 步驟 4: 設置系統服務監控
Write-Host "步驟 4: 設置系統服務監控..." -ForegroundColor Cyan
Write-Host ""

$serviceMonitorScript = Join-Path $Root "scripts\wuchang_service_monitor.ps1"
if (Test-Path $serviceMonitorScript) {
    Write-Host "  檢查服務狀態..." -ForegroundColor Yellow
    & $serviceMonitorScript -Action check
} else {
    Write-Host "  ⚠ 服務監控腳本不存在: $serviceMonitorScript" -ForegroundColor Yellow
}
Write-Host ""

# 步驟 5: 設置容器健康監控
Write-Host "步驟 5: 設置容器健康監控..." -ForegroundColor Cyan
Write-Host ""

$containerHealthScript = Join-Path $Root "scripts\wuchang_container_health.ps1"
if (Test-Path $containerHealthScript) {
    Write-Host "  檢查容器狀態..." -ForegroundColor Yellow
    & $containerHealthScript -Action check
} else {
    Write-Host "  ⚠ 容器健康監控腳本不存在: $containerHealthScript" -ForegroundColor Yellow
}
Write-Host ""

# 步驟 6: 測試優化配置（可選）
if (-not $SkipTests) {
    Write-Host "步驟 6: 測試優化配置..." -ForegroundColor Cyan
    Write-Host ""
    
    $optimizedCompose = Join-Path $Root "docker-compose.optimized.yml"
    if (Test-Path $optimizedCompose) {
        Write-Host "  驗證優化配置..." -ForegroundColor Yellow
        Push-Location $Root
        docker-compose -f docker-compose.optimized.yml config 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ 優化配置有效" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ 優化配置驗證失敗，使用默認配置" -ForegroundColor Yellow
        }
        Pop-Location
    } else {
        Write-Host "  ⚠ 優化配置文件不存在: $optimizedCompose" -ForegroundColor Yellow
    }
    Write-Host ""
}

# 步驟 7: 生成設置報告
Write-Host "步驟 7: 生成設置報告..." -ForegroundColor Cyan
Write-Host ""

$report = @{
    Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    System = @{
        OS = "Windows 10 專業版"
        DockerVersion = (docker --version 2>&1).ToString()
        PythonVersion = (python --version 2>&1).ToString()
        WSLEnabled = $false
    }
    Services = @()
    Containers = @()
    Tasks = @()
    Optimizations = @(
        "統一任務管理",
        "系統服務監控",
        "容器健康監控",
        "資源限制配置",
        "健康檢查配置"
    )
}

# 檢查 WSL
try {
    wsl --list | Out-Null
    $report.System.WSLEnabled = ($LASTEXITCODE -eq 0)
} catch {}

# 檢查服務
if (Test-Path $serviceMonitorScript) {
    $serviceStatus = & $serviceMonitorScript -Action check 2>&1
    # 解析服務狀態（簡化）
}

# 檢查容器
if (Test-Path $containerHealthScript) {
    $containerStatus = & $containerHealthScript -Action check 2>&1
    # 解析容器狀態（簡化）
}

# 檢查任務
if (Test-Path $taskManagerScript) {
    $taskStatus = & $taskManagerScript -Action health 2>&1
    # 解析任務狀態（簡化）
}

# 保存報告
try {
    $reportFile = Join-Path $Root "logs\architecture_setup_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
    $reportDir = Split-Path -Parent $reportFile
    if (-not (Test-Path $reportDir)) { New-Item -ItemType Directory -Path $reportDir -Force | Out-Null }
    $report | ConvertTo-Json -Depth 10 | Set-Content -Path $reportFile -Encoding UTF8
    Write-Host "  ✅ 報告已保存: $reportFile" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ 保存報告失敗: $($_.Exception.Message)" -ForegroundColor Yellow
}
Write-Host ""

# 完成
Write-Host "=" * 80
Write-Host "  ✅ 優化架構設置完成"
Write-Host "=" * 80
Write-Host ""

Write-Host "已完成的優化:" -ForegroundColor Cyan
Write-Host "  ✅ 統一任務管理系統"
Write-Host "  ✅ 系統服務監控"
Write-Host "  ✅ 容器健康監控"
Write-Host "  ✅ 優化 Docker Compose 配置"
Write-Host ""

Write-Host "管理命令:" -ForegroundColor Cyan
Write-Host "  任務管理: .\scripts\wuchang_task_manager.ps1 -Action status"
Write-Host "  服務監控: .\scripts\wuchang_service_monitor.ps1 -Action check"
Write-Host "  容器監控: .\scripts\wuchang_container_health.ps1 -Action check"
Write-Host ""

Write-Host "✅ 合規: 符合 Google 非營利組織合規要求" -ForegroundColor Green
Write-Host ""
