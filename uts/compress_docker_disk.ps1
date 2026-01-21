# 壓縮 Docker 虛擬硬碟
# compress_docker_disk.ps1

Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "Docker 虛擬硬碟壓縮工具" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host ""

# 檢查管理員權限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "警告: 需要管理員權限來壓縮虛擬硬碟" -ForegroundColor Yellow
    Write-Host "正在請求提升權限..." -ForegroundColor Yellow
    Write-Host ""
    
    $scriptPath = $MyInvocation.MyCommand.Path
    Start-Process powershell.exe -Verb RunAs -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$scriptPath`"" -Wait
    exit
}

Write-Host "已具有管理員權限" -ForegroundColor Green
Write-Host ""

# 檢查 Docker 虛擬硬碟路徑
$dockerVHDX = "$env:USERPROFILE\AppData\Local\Docker\wsl\disk\docker_data.vhdx"

if (-not (Test-Path $dockerVHDX)) {
    Write-Host "錯誤: 找不到 Docker 虛擬硬碟" -ForegroundColor Red
    Write-Host "路徑: $dockerVHDX" -ForegroundColor Yellow
    exit 1
}

# 獲取壓縮前大小
$beforeSize = (Get-Item $dockerVHDX).Length / 1GB
Write-Host "Docker 虛擬硬碟: $dockerVHDX" -ForegroundColor Cyan
Write-Host "壓縮前大小: $([math]::Round($beforeSize, 2)) GB" -ForegroundColor Cyan
Write-Host ""

# 1. 停止 Docker Desktop
Write-Host "【步驟 1】停止 Docker Desktop..." -ForegroundColor Yellow
Write-Host ""

$dockerProcesses = Get-Process -Name "Docker Desktop", "com.docker.backend", "dockerd" -ErrorAction SilentlyContinue
if ($dockerProcesses) {
    Write-Host "找到 Docker 進程，正在停止..." -ForegroundColor Yellow
    foreach ($proc in $dockerProcesses) {
        try {
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            Write-Host "  已停止: $($proc.ProcessName)" -ForegroundColor Green
        } catch {
            Write-Host "  停止失敗: $($proc.ProcessName)" -ForegroundColor Yellow
        }
    }
    Start-Sleep -Seconds 3
} else {
    Write-Host "未找到運行中的 Docker 進程" -ForegroundColor Green
}
Write-Host ""

# 2. 關閉 WSL
Write-Host "【步驟 2】關閉 WSL..." -ForegroundColor Yellow
Write-Host ""

try {
    Write-Host "正在執行 wsl --shutdown..." -ForegroundColor Yellow
    wsl --shutdown 2>&1 | Out-Null
    Start-Sleep -Seconds 5
    Write-Host "WSL 已關閉" -ForegroundColor Green
} catch {
    Write-Host "關閉 WSL 時發生錯誤: $_" -ForegroundColor Yellow
}
Write-Host ""

# 3. 確認 Docker 虛擬硬碟未被使用
Write-Host "【步驟 3】確認虛擬硬碟未被使用..." -ForegroundColor Yellow
Write-Host ""

$retryCount = 0
$maxRetries = 5
$canOptimize = $false

while ($retryCount -lt $maxRetries) {
    try {
        # 嘗試以只讀模式打開檔案來確認未被使用
        $file = [System.IO.File]::Open($dockerVHDX, 'Open', 'Read', 'None')
        $file.Close()
        $canOptimize = $true
        Write-Host "虛擬硬碟可以壓縮" -ForegroundColor Green
        break
    } catch {
        $retryCount++
        if ($retryCount -lt $maxRetries) {
            Write-Host "虛擬硬碟可能正在使用中，等待 3 秒後重試 ($retryCount/$maxRetries)..." -ForegroundColor Yellow
            Start-Sleep -Seconds 3
        } else {
            Write-Host "警告: 無法確認虛擬硬碟是否可用，將繼續嘗試壓縮" -ForegroundColor Yellow
        }
    }
}
Write-Host ""

# 4. 執行壓縮
Write-Host "【步驟 4】壓縮 Docker 虛擬硬碟..." -ForegroundColor Yellow
Write-Host ""
Write-Host "這可能需要 10-30 分鐘，請耐心等待..." -ForegroundColor Yellow
Write-Host "壓縮過程中請勿關閉此視窗" -ForegroundColor Yellow
Write-Host ""

try {
    $startTime = Get-Date
    Optimize-VHD -Path $dockerVHDX -Mode Full -ErrorAction Stop
    
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalMinutes
    
    Write-Host "壓縮完成！" -ForegroundColor Green
    Write-Host "耗時: $([math]::Round($duration, 1)) 分鐘" -ForegroundColor Cyan
    Write-Host ""
    
    # 獲取壓縮後大小
    $afterSize = (Get-Item $dockerVHDX).Length / 1GB
    $saved = $beforeSize - $afterSize
    
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host "壓縮結果" -ForegroundColor Cyan
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host ""
    Write-Host "壓縮前大小: $([math]::Round($beforeSize, 2)) GB" -ForegroundColor Yellow
    Write-Host "壓縮後大小: $([math]::Round($afterSize, 2)) GB" -ForegroundColor Green
    Write-Host "節省空間: $([math]::Round($saved, 2)) GB" -ForegroundColor Green
    Write-Host ""
    
} catch {
    Write-Host "壓縮失敗: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "可能的原因：" -ForegroundColor Yellow
    Write-Host "  1. 虛擬硬碟正在使用中（請確保 Docker Desktop 已完全關閉）" -ForegroundColor Yellow
    Write-Host "  2. 需要重啟電腦後再試" -ForegroundColor Yellow
    Write-Host "  3. 權限不足" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "手動執行命令：" -ForegroundColor Yellow
    Write-Host "  Optimize-VHD -Path `"$dockerVHDX`" -Mode Full" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

Write-Host "注意: 壓縮完成後，可以重新啟動 Docker Desktop" -ForegroundColor Yellow
Write-Host ""
