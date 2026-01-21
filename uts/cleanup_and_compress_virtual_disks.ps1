# 清理和壓縮虛擬硬碟
# cleanup_and_compress_virtual_disks.ps1

Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "虛擬硬碟清理和壓縮工具" -ForegroundColor Cyan
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

# 1. 清理 Docker
Write-Host "【步驟 1】清理 Docker..." -ForegroundColor Yellow
Write-Host ""

try {
    Write-Host "檢查 Docker 使用情況..." -ForegroundColor Cyan
    $dockerDF = docker system df 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host $dockerDF
        Write-Host ""
        
        Write-Host "正在清理未使用的 Docker 資源..." -ForegroundColor Yellow
        docker system prune -a --volumes -f 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Docker 清理完成" -ForegroundColor Green
        } else {
            Write-Host "Docker 清理失敗或 Docker 未運行" -ForegroundColor Yellow
        }
    } else {
        Write-Host "Docker 未運行或未安裝" -ForegroundColor Yellow
    }
} catch {
    Write-Host "無法執行 Docker 命令: $_" -ForegroundColor Yellow
}
Write-Host ""

# 2. 壓縮 Docker 虛擬硬碟
Write-Host "【步驟 2】壓縮 Docker 虛擬硬碟..." -ForegroundColor Yellow
Write-Host ""

$dockerVHDX = "$env:USERPROFILE\AppData\Local\Docker\wsl\disk\docker_data.vhdx"

if (Test-Path $dockerVHDX) {
    $beforeSize = (Get-Item $dockerVHDX).Length / 1GB
    
    Write-Host "Docker 虛擬硬碟: $dockerVHDX" -ForegroundColor Cyan
    Write-Host "  壓縮前大小: $([math]::Round($beforeSize, 2)) GB" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "正在停止 Docker..." -ForegroundColor Yellow
    wsl --shutdown 2>&1 | Out-Null
    Start-Sleep -Seconds 3
    
    Write-Host "正在壓縮虛擬硬碟（這可能需要幾分鐘）..." -ForegroundColor Yellow
    try {
        Optimize-VHD -Path $dockerVHDX -Mode Full -ErrorAction Stop
        Write-Host "Docker 虛擬硬碟壓縮完成" -ForegroundColor Green
        
        $afterSize = (Get-Item $dockerVHDX).Length / 1GB
        $saved = $beforeSize - $afterSize
        Write-Host "  壓縮後大小: $([math]::Round($afterSize, 2)) GB" -ForegroundColor Green
        Write-Host "  節省空間: $([math]::Round($saved, 2)) GB" -ForegroundColor Green
    } catch {
        Write-Host "壓縮失敗: $_" -ForegroundColor Red
        Write-Host "可能需要手動執行: Optimize-VHD -Path `"$dockerVHDX`" -Mode Full" -ForegroundColor Yellow
    }
} else {
    Write-Host "未找到 Docker 虛擬硬碟" -ForegroundColor Yellow
}
Write-Host ""

# 3. 壓縮 WSL 虛擬硬碟
Write-Host "【步驟 3】壓縮 WSL 虛擬硬碟..." -ForegroundColor Yellow
Write-Host ""

$wslBase = "$env:USERPROFILE\AppData\Local\wsl"
$wslVHDXs = Get-ChildItem $wslBase -Recurse -Filter "*.vhdx" -ErrorAction SilentlyContinue

if ($wslVHDXs) {
    Write-Host "確保 WSL 已關閉..." -ForegroundColor Yellow
    wsl --shutdown 2>&1 | Out-Null
    Start-Sleep -Seconds 3
    
    foreach ($vhdx in $wslVHDXs) {
        $beforeSize = $vhdx.Length / 1GB
        
        Write-Host "WSL 虛擬硬碟: $($vhdx.FullName)" -ForegroundColor Cyan
        Write-Host "  壓縮前大小: $([math]::Round($beforeSize, 2)) GB" -ForegroundColor Cyan
        Write-Host ""
        
        Write-Host "正在壓縮..." -ForegroundColor Yellow
        try {
            Optimize-VHD -Path $vhdx.FullName -Mode Full -ErrorAction Stop
            Write-Host "WSL 虛擬硬碟壓縮完成" -ForegroundColor Green
            
            $afterSize = (Get-Item $vhdx.FullName).Length / 1GB
            $saved = $beforeSize - $afterSize
            Write-Host "  壓縮後大小: $([math]::Round($afterSize, 2)) GB" -ForegroundColor Green
            Write-Host "  節省空間: $([math]::Round($saved, 2)) GB" -ForegroundColor Green
        } catch {
            Write-Host "壓縮失敗: $_" -ForegroundColor Red
        }
        Write-Host ""
    }
} else {
    Write-Host "未找到 WSL 虛擬硬碟" -ForegroundColor Yellow
}
Write-Host ""

# 總結
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "清理和壓縮完成" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host ""

Write-Host "注意事項：" -ForegroundColor Yellow
Write-Host "  1. 虛擬硬碟壓縮需要時間，請耐心等待" -ForegroundColor Yellow
Write-Host "  2. 壓縮後可能需要重啟 Docker/WSL" -ForegroundColor Yellow
Write-Host "  3. 如果壓縮失敗，可能是檔案正在使用，請重啟後再試" -ForegroundColor Yellow
Write-Host ""
