# ============================================
# Docker Desktop 中文化設定腳本
# ============================================

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Docker Desktop 中文化設定" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 檢查 Docker Desktop 是否正在運行
$dockerProcess = Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue
if ($dockerProcess) {
    Write-Host "⚠ 偵測到 Docker Desktop 正在運行" -ForegroundColor Yellow
    Write-Host "請先關閉 Docker Desktop（系統托盤右鍵 → Quit Docker Desktop）" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "是否已關閉 Docker Desktop？(Y/N)"
    if ($continue -ne "Y" -and $continue -ne "y") {
        Write-Host "操作已取消" -ForegroundColor Red
        exit
    }
}

# Docker Desktop 資源目錄路徑
$dockerResourcesPath = "C:\Program Files\Docker\Docker\resources"
$appAsarPath = Join-Path $dockerResourcesPath "app.asar"
$appAsarBackupPath = Join-Path $dockerResourcesPath "app.asar.backup"

# 檢查 Docker Desktop 是否已安裝
if (-not (Test-Path $appAsarPath)) {
    Write-Host "❌ 找不到 Docker Desktop 安裝目錄" -ForegroundColor Red
    Write-Host "路徑: $appAsarPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "請確認 Docker Desktop 已正確安裝" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ 找到 Docker Desktop 安裝目錄" -ForegroundColor Green
Write-Host "路徑: $dockerResourcesPath" -ForegroundColor Gray
Write-Host ""

# 檢查是否已有備份
$hasBackup = Test-Path $appAsarBackupPath
if ($hasBackup) {
    Write-Host "⚠ 偵測到已存在備份檔案" -ForegroundColor Yellow
    Write-Host "備份路徑: $appAsarBackupPath" -ForegroundColor Gray
    Write-Host ""
    $restore = Read-Host "是否要還原為原始英文版本？(Y/N)"
    if ($restore -eq "Y" -or $restore -eq "y") {
        Write-Host ""
        Write-Host "正在還原原始檔案..." -ForegroundColor Cyan
        try {
            Copy-Item -Path $appAsarBackupPath -Destination $appAsarPath -Force
            Write-Host "✓ 已還原為原始英文版本" -ForegroundColor Green
            Write-Host ""
            Write-Host "請重新啟動 Docker Desktop 以套用變更" -ForegroundColor Yellow
            exit 0
        } catch {
            Write-Host "❌ 還原失敗: $_" -ForegroundColor Red
            exit 1
        }
    }
}

# 建立備份目錄（如果不存在）
$backupDir = Join-Path $PSScriptRoot "docker_desktop_backup"
if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
}

# 備份原始檔案
Write-Host "正在備份原始檔案..." -ForegroundColor Cyan
try {
    # 備份到資源目錄
    Copy-Item -Path $appAsarPath -Destination $appAsarBackupPath -Force
    # 備份到腳本目錄（額外備份）
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $scriptBackupPath = Join-Path $backupDir "app.asar.backup_$timestamp"
    Copy-Item -Path $appAsarPath -Destination $scriptBackupPath -Force
    Write-Host "✓ 備份完成" -ForegroundColor Green
    Write-Host "  資源目錄備份: $appAsarBackupPath" -ForegroundColor Gray
    Write-Host "  腳本目錄備份: $scriptBackupPath" -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "❌ 備份失敗: $_" -ForegroundColor Red
    exit 1
}

# 下載漢化包
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "下載漢化包" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 獲取 Docker Desktop 版本
$dockerVersion = (Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Docker Desktop").DisplayVersion -ErrorAction SilentlyContinue
if ($dockerVersion) {
    Write-Host "偵測到 Docker Desktop 版本: $dockerVersion" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "請選擇下載方式：" -ForegroundColor Yellow
Write-Host "1. 自動從 GitHub 下載（推薦）" -ForegroundColor White
Write-Host "2. 手動下載後指定檔案路徑" -ForegroundColor White
Write-Host ""
$choice = Read-Host "請選擇 (1/2)"

$chineseAsarPath = $null

if ($choice -eq "1") {
    # 自動下載
    Write-Host ""
    Write-Host "正在從 GitHub 下載漢化包..." -ForegroundColor Cyan
    
    $repoUrl = "https://github.com/asxez/DockerDesktop-CN"
    Write-Host "漢化包來源: $repoUrl" -ForegroundColor Gray
    Write-Host ""
    Write-Host "⚠ 注意：由於需要選擇對應版本的漢化包，" -ForegroundColor Yellow
    Write-Host "   建議您手動前往以下網址下載：" -ForegroundColor Yellow
    Write-Host "   $repoUrl/releases" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   或使用以下 PowerShell 命令下載最新版本：" -ForegroundColor Yellow
    Write-Host "   Invoke-WebRequest -Uri 'https://github.com/asxez/DockerDesktop-CN/releases/latest/download/app.asar' -OutFile 'app.asar'" -ForegroundColor Gray
    Write-Host ""
    
    $autoDownload = Read-Host "是否要自動下載最新版本？(Y/N)"
    if ($autoDownload -eq "Y" -or $autoDownload -eq "y") {
        try {
            $downloadPath = Join-Path $backupDir "app.asar.chinese"
            $downloadUrl = "https://github.com/asxez/DockerDesktop-CN/releases/latest/download/app.asar"
            Write-Host "正在下載: $downloadUrl" -ForegroundColor Cyan
            Invoke-WebRequest -Uri $downloadUrl -OutFile $downloadPath -UseBasicParsing
            Write-Host "✓ 下載完成" -ForegroundColor Green
            $chineseAsarPath = $downloadPath
        } catch {
            Write-Host "❌ 下載失敗: $_" -ForegroundColor Red
            Write-Host "請改用手動下載方式" -ForegroundColor Yellow
            $choice = "2"
        }
    } else {
        $choice = "2"
    }
}

if ($choice -eq "2" -or $chineseAsarPath -eq $null) {
    # 手動指定路徑
    Write-Host ""
    Write-Host "請輸入漢化包檔案路徑（app.asar）" -ForegroundColor Yellow
    Write-Host "或直接將檔案拖放到此視窗" -ForegroundColor Gray
    Write-Host ""
    $inputPath = Read-Host "檔案路徑"
    
    # 處理拖放路徑（移除引號）
    $inputPath = $inputPath.Trim('"')
    
    if (-not (Test-Path $inputPath)) {
        Write-Host "❌ 找不到檔案: $inputPath" -ForegroundColor Red
        exit 1
    }
    
    $chineseAsarPath = $inputPath
}

# 驗證檔案
Write-Host ""
Write-Host "正在驗證檔案..." -ForegroundColor Cyan
if (-not (Test-Path $chineseAsarPath)) {
    Write-Host "❌ 找不到漢化包檔案" -ForegroundColor Red
    exit 1
}

$fileInfo = Get-Item $chineseAsarPath
Write-Host "✓ 檔案大小: $([math]::Round($fileInfo.Length / 1MB, 2)) MB" -ForegroundColor Green
Write-Host ""

# 替換檔案
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "套用漢化包" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "⚠ 即將替換 Docker Desktop 資源檔案" -ForegroundColor Yellow
Write-Host "   原始檔案已備份至: $appAsarBackupPath" -ForegroundColor Gray
Write-Host ""
$confirm = Read-Host "確認繼續？(Y/N)"

if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "操作已取消" -ForegroundColor Yellow
    exit
}

Write-Host ""
Write-Host "正在套用漢化包..." -ForegroundColor Cyan
try {
    # 確保 Docker Desktop 已關閉
    $dockerProcess = Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue
    if ($dockerProcess) {
        Write-Host "⚠ 偵測到 Docker Desktop 仍在運行，正在嘗試關閉..." -ForegroundColor Yellow
        Stop-Process -Name "Docker Desktop" -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
    
    # 複製漢化包
    Copy-Item -Path $chineseAsarPath -Destination $appAsarPath -Force
    Write-Host "✓ 漢化包已成功套用" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "✓ 中文化完成！" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "請重新啟動 Docker Desktop 以查看中文介面" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "備份資訊：" -ForegroundColor Cyan
    Write-Host "  - 資源目錄備份: $appAsarBackupPath" -ForegroundColor Gray
    Write-Host "  - 腳本目錄備份: $scriptBackupPath" -ForegroundColor Gray
    Write-Host ""
    Write-Host "如需還原為英文版本，請重新執行此腳本並選擇還原選項" -ForegroundColor Gray
    Write-Host ""
    
    $startNow = Read-Host "是否現在啟動 Docker Desktop？(Y/N)"
    if ($startNow -eq "Y" -or $startNow -eq "y") {
        Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
        Write-Host "✓ 正在啟動 Docker Desktop..." -ForegroundColor Green
    }
    
} catch {
    Write-Host "❌ 套用失敗: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "正在嘗試還原備份..." -ForegroundColor Yellow
    try {
        Copy-Item -Path $appAsarBackupPath -Destination $appAsarPath -Force
        Write-Host "✓ 已還原原始檔案" -ForegroundColor Green
    } catch {
        Write-Host "❌ 還原失敗，請手動從備份還原: $appAsarBackupPath" -ForegroundColor Red
    }
    exit 1
}
