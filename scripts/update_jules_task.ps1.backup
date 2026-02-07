# 更新 Jules 任務 URL 並開啟
# 用於設定新的 Jules 任務連結並進行同步

param(
    [Parameter(Mandatory=$true)]
    [string]$TaskUrl,
    
    [Parameter(Mandatory=$false)]
    [switch]$OpenBrowser = $true,
    
    [Parameter(Mandatory=$false)]
    [switch]$SyncAfterUpdate = $false
)

$root = (Get-Location).Path
$urlFile = Join-Path $root "config\jules.url.txt"
$syncScript = Join-Path $root "scripts\jules_sync.ps1"

Write-Host "=== 更新 Jules 任務 URL ===" -ForegroundColor Cyan

# 1. 確保 config 目錄存在
$configDir = Split-Path -Parent $urlFile
if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    Write-Host "  ✓ 已建立 config 目錄" -ForegroundColor Green
}

# 2. 保存新的 URL
Write-Host "`n[1] 更新 Jules 任務 URL..." -ForegroundColor Yellow
Set-Content -Path $urlFile -Value $TaskUrl -Encoding ASCII
Write-Host "  ✓ 已更新: $urlFile" -ForegroundColor Green
Write-Host "  URL: $TaskUrl" -ForegroundColor Cyan

# 3. 提取任務 ID
$taskId = ""
if ($TaskUrl -match "task/(\d+)") {
    $taskId = $matches[1]
    Write-Host "  ✓ 任務 ID: $taskId" -ForegroundColor Green
} else {
    Write-Host "  ⚠ 無法提取任務 ID" -ForegroundColor Yellow
}

# 4. 開啟瀏覽器（如果需要）
if ($OpenBrowser) {
    Write-Host "`n[2] 開啟 Jules 任務連結..." -ForegroundColor Yellow
    try {
        Start-Process $TaskUrl
        Write-Host "  ✓ 已開啟瀏覽器" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ 無法開啟瀏覽器: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 5. 執行同步（如果需要）
if ($SyncAfterUpdate) {
    Write-Host "`n[3] 執行 Jules 同步..." -ForegroundColor Yellow
    if (Test-Path $syncScript) {
        try {
            $outPath = & $syncScript
            Write-Host "  ✓ 同步完成" -ForegroundColor Green
            if ($outPath) {
                Write-Host "  輸出檔案: $outPath" -ForegroundColor Cyan
            }
        } catch {
            Write-Host "  ❌ 同步失敗: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "  ⚠ 同步腳本不存在: $syncScript" -ForegroundColor Yellow
    }
}

Write-Host "`n=== 更新完成 ===" -ForegroundColor Green

Write-Host "`n後續步驟：" -ForegroundColor Yellow
Write-Host "  1. 在瀏覽器中完成 Google 登入" -ForegroundColor White
Write-Host "  2. 如果需要同步，執行: .\scripts\jules_sync.ps1" -ForegroundColor White
Write-Host "  3. 或使用: .\scripts\auto_jules_authorize_and_sync.ps1" -ForegroundColor White
