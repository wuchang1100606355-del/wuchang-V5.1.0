# 五常 AI - 啟動雲端同步服務

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  🌐 五常 AI - 雲端智能同步服務" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# 切換到正確目錄
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# 檢查 Python
Write-Host "檢查環境..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "❌ 找不到 Python" -ForegroundColor Red
    exit 1
}

Write-Host "  ✅ Python 環境正常" -ForegroundColor Green
Write-Host ""

# 檢查依賴
$requiredPackages = @("aiofiles", "psutil")
$missingPackages = @()

foreach ($pkg in $requiredPackages) {
    $installed = & python -c "import $pkg" 2>&1
    if ($LASTEXITCODE -ne 0) {
        $missingPackages += $pkg
    }
}

if ($missingPackages.Count -gt 0) {
    Write-Host "⚠️  安裝缺少的套件..." -ForegroundColor Yellow
    foreach ($pkg in $missingPackages) {
        Write-Host "  安裝 $pkg..." -ForegroundColor Gray
        & python -m pip install $pkg --quiet
    }
    Write-Host "  ✅ 依賴安裝完成" -ForegroundColor Green
}

Write-Host ""

# 檢測當前角色
Write-Host "檢測當前角色..." -ForegroundColor Yellow
$interfaces = Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.50.*"}

$role = "未知"
$peerIP = ""

foreach ($interface in $interfaces) {
    if ($interface.IPAddress -eq "192.168.50.84") {
        $role = "本機 (192.168.50.84)"
        $peerIP = "192.168.50.249"
        break
    } elseif ($interface.IPAddress -eq "192.168.50.249") {
        $role = "Server (192.168.50.249)"
        $peerIP = "192.168.50.84"
        break
    }
}

Write-Host "  角色: $role" -ForegroundColor White
Write-Host "  對方: $peerIP" -ForegroundColor White
Write-Host ""

# 檢查連通性
Write-Host "檢查雲端連通性..." -ForegroundColor Yellow
$pingResult = Test-Connection -ComputerName $peerIP -Count 1 -Quiet -ErrorAction SilentlyContinue

if ($pingResult) {
    Write-Host "  ✅ 雙方雲端可見" -ForegroundColor Green
} else {
    Write-Host "  ❌ 對方不可達 ($peerIP)" -ForegroundColor Red
    Write-Host ""
    Write-Host "無法進行同步，請檢查:" -ForegroundColor Yellow
    Write-Host "  1. 網路連線" -ForegroundColor White
    Write-Host "  2. 防火牆設置" -ForegroundColor White
    Write-Host "  3. 對方是否在線" -ForegroundColor White
    Write-Host ""
    Read-Host "按 Enter 退出"
    exit 1
}

Write-Host ""

# 選擇運行模式
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  請選擇同步模式" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  1. 試運行（只查看同步計劃，不執行）" -ForegroundColor White
Write-Host "  2. 互動模式（確認後執行）" -ForegroundColor White
Write-Host "  3. 自動模式（直接執行）" -ForegroundColor White
Write-Host "  4. 持續監控模式（自動偵測變更並同步）" -ForegroundColor White
Write-Host ""

$mode = Read-Host "請輸入選項 (1-4)"

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  🚀 啟動同步服務..." -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

switch ($mode) {
    "1" {
        Write-Host "🔍 試運行模式 - 只顯示同步計劃" -ForegroundColor Yellow
        Write-Host ""
        & python cloud_sync_service.py --dry-run
    }
    "2" {
        Write-Host "💬 互動模式 - 需要確認才執行" -ForegroundColor Yellow
        Write-Host ""
        & python cloud_sync_service.py
    }
    "3" {
        Write-Host "⚡ 自動模式 - 立即執行同步" -ForegroundColor Yellow
        Write-Host ""
        & python cloud_sync_service.py --auto
    }
    "4" {
        Write-Host "👁️  持續監控模式 - 自動偵測變更" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "此功能開發中..." -ForegroundColor Gray
        Write-Host ""
        Write-Host "目前建議使用計劃任務定期執行同步:" -ForegroundColor Yellow
        Write-Host "  1. 打開「工作排程器」" -ForegroundColor White
        Write-Host "  2. 創建新任務" -ForegroundColor White
        Write-Host "  3. 觸發程式: powershell" -ForegroundColor White
        Write-Host "  4. 參數: -File `"$PSCommandPath`" -Mode 3" -ForegroundColor White
        Write-Host "  5. 設定每 5 分鐘執行一次" -ForegroundColor White
    }
    default {
        Write-Host "❌ 無效的選項" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  完成" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""
