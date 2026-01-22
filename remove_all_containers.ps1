# ============================================
# 完整卸載全部 Docker 容器腳本
# ============================================

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Red
Write-Host "完整卸載全部 Docker 容器" -ForegroundColor Red
Write-Host "============================================" -ForegroundColor Red
Write-Host ""

# 檢查 Docker 是否可用
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Docker 未安裝或無法使用"
    }
    Write-Host "✓ Docker 已安裝: $dockerVersion" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ Docker 未安裝或無法使用" -ForegroundColor Red
    Write-Host "請先安裝 Docker Desktop" -ForegroundColor Yellow
    exit 1
}

# 檢查是否有容器
Write-Host "正在檢查容器狀態..." -ForegroundColor Cyan
$allContainers = docker ps -a --format "{{.Names}}" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 無法查詢容器列表" -ForegroundColor Red
    exit 1
}

$containerList = $allContainers | Where-Object { $_ -ne "" }
$containerCount = ($containerList | Measure-Object).Count

if ($containerCount -eq 0) {
    Write-Host "✓ 沒有找到任何容器" -ForegroundColor Green
    exit 0
}

Write-Host "找到 $containerCount 個容器：" -ForegroundColor Yellow
Write-Host ""

# 顯示容器列表
$runningContainers = docker ps --format "{{.Names}}" 2>&1
$runningList = $runningContainers | Where-Object { $_ -ne "" }
$runningCount = ($runningList | Measure-Object).Count

if ($runningCount -gt 0) {
    Write-Host "正在運行的容器 ($runningCount 個)：" -ForegroundColor Yellow
    docker ps --format "  - {{.Names}} ({{.Status}})" 2>&1 | ForEach-Object { Write-Host $_ -ForegroundColor White }
    Write-Host ""
}

$stoppedContainers = docker ps -a --filter "status=exited" --format "{{.Names}}" 2>&1
$stoppedList = $stoppedContainers | Where-Object { $_ -ne "" }
$stoppedCount = ($stoppedList | Measure-Object).Count

if ($stoppedCount -gt 0) {
    Write-Host "已停止的容器 ($stoppedCount 個)：" -ForegroundColor Gray
    docker ps -a --filter "status=exited" --format "  - {{.Names}} ({{.Status}})" 2>&1 | ForEach-Object { Write-Host $_ -ForegroundColor Gray }
    Write-Host ""
}

# 警告提示
Write-Host "============================================" -ForegroundColor Red
Write-Host "⚠ 警告：此操作將執行以下操作：" -ForegroundColor Red
Write-Host "============================================" -ForegroundColor Red
Write-Host "1. 停止所有正在運行的容器" -ForegroundColor Yellow
Write-Host "2. 刪除所有容器（包括已停止的）" -ForegroundColor Yellow
Write-Host "3. 可選：刪除未使用的映像、網路、卷" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠ 此操作無法復原！" -ForegroundColor Red
Write-Host ""

$confirm = Read-Host "確認要刪除所有容器嗎？(輸入 'YES' 確認)"

if ($confirm -ne "YES") {
    Write-Host "操作已取消" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "開始卸載容器" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 步驟 1: 停止所有正在運行的容器
Write-Host "[1/3] 正在停止所有容器..." -ForegroundColor Cyan
try {
    if ($runningCount -gt 0) {
        docker stop $(docker ps -q) 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ 已停止 $runningCount 個容器" -ForegroundColor Green
        } else {
            Write-Host "⚠ 部分容器停止失敗（可能已停止）" -ForegroundColor Yellow
        }
    } else {
        Write-Host "✓ 沒有正在運行的容器" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠ 停止容器時發生錯誤: $_" -ForegroundColor Yellow
}

Write-Host ""

# 步驟 2: 刪除所有容器
Write-Host "[2/3] 正在刪除所有容器..." -ForegroundColor Cyan
try {
    docker rm $(docker ps -a -q) 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ 已刪除所有容器" -ForegroundColor Green
    } else {
        Write-Host "⚠ 部分容器刪除失敗" -ForegroundColor Yellow
        # 嘗試強制刪除
        Write-Host "  正在嘗試強制刪除..." -ForegroundColor Yellow
        docker rm -f $(docker ps -a -q) 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ 已強制刪除所有容器" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "❌ 刪除容器時發生錯誤: $_" -ForegroundColor Red
}

Write-Host ""

# 步驟 3: 可選清理
Write-Host "[3/3] 清理選項" -ForegroundColor Cyan
Write-Host ""
Write-Host "是否要清理以下項目？" -ForegroundColor Yellow
Write-Host "1. 刪除未使用的映像（dangling images）" -ForegroundColor White
Write-Host "2. 刪除未使用的網路" -ForegroundColor White
Write-Host "3. 刪除未使用的卷（volumes）" -ForegroundColor White
Write-Host "4. 執行完整清理（以上全部）" -ForegroundColor White
Write-Host "5. 跳過清理" -ForegroundColor White
Write-Host ""
$cleanChoice = Read-Host "請選擇 (1-5)"

switch ($cleanChoice) {
    "1" {
        Write-Host ""
        Write-Host "正在刪除未使用的映像..." -ForegroundColor Cyan
        docker image prune -f 2>&1 | Out-Null
        Write-Host "✓ 已清理未使用的映像" -ForegroundColor Green
    }
    "2" {
        Write-Host ""
        Write-Host "正在刪除未使用的網路..." -ForegroundColor Cyan
        docker network prune -f 2>&1 | Out-Null
        Write-Host "✓ 已清理未使用的網路" -ForegroundColor Green
    }
    "3" {
        Write-Host ""
        Write-Host "⚠ 警告：刪除卷將永久刪除所有數據！" -ForegroundColor Red
        $volumeConfirm = Read-Host "確認刪除未使用的卷？(輸入 'YES' 確認)"
        if ($volumeConfirm -eq "YES") {
            docker volume prune -f 2>&1 | Out-Null
            Write-Host "✓ 已清理未使用的卷" -ForegroundColor Green
        } else {
            Write-Host "已跳過卷清理" -ForegroundColor Yellow
        }
    }
    "4" {
        Write-Host ""
        Write-Host "⚠ 警告：完整清理將刪除所有未使用的映像和卷！" -ForegroundColor Red
        $fullConfirm = Read-Host "確認執行完整清理？(輸入 'YES' 確認)"
        if ($fullConfirm -eq "YES") {
            Write-Host "正在執行完整清理..." -ForegroundColor Cyan
            docker system prune -a -f --volumes 2>&1 | Out-Null
            Write-Host "✓ 已執行完整清理（包括所有未使用的映像、網路和卷）" -ForegroundColor Green
            Write-Host "⚠ 注意：此操作已刪除所有未使用的映像和卷" -ForegroundColor Yellow
        } else {
            Write-Host "已跳過完整清理" -ForegroundColor Yellow
        }
    }
    default {
        Write-Host "已跳過清理" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "✓ 卸載完成！" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

# 驗證結果
Write-Host "驗證結果：" -ForegroundColor Cyan
$remainingContainers = docker ps -a --format "{{.Names}}" 2>&1
$remainingList = $remainingContainers | Where-Object { $_ -ne "" }
$remainingCount = ($remainingList | Measure-Object).Count

if ($remainingCount -eq 0) {
    Write-Host "✓ 所有容器已成功刪除" -ForegroundColor Green
} else {
    Write-Host "⚠ 仍有 $remainingCount 個容器存在：" -ForegroundColor Yellow
    docker ps -a --format "  - {{.Names}}" 2>&1 | ForEach-Object { Write-Host $_ -ForegroundColor Yellow }
    Write-Host ""
    Write-Host "如需強制刪除，請手動執行：" -ForegroundColor Yellow
    Write-Host "  docker rm -f `$(docker ps -a -q)" -ForegroundColor Gray
}

Write-Host ""
