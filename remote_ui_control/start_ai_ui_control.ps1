# 五常 AI - AI 智能 UI 控制系統啟動腳本
# Server 端 (192.168.50.249)

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  🤖 五常 AI - 智能 UI 控制系統" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "小j 能夠理解你的需求，智能地控制本機 UI" -ForegroundColor Yellow
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

Write-Host "✅ Python 環境正常" -ForegroundColor Green
Write-Host ""

# 檢查依賴
$requiredPackages = @("vertexai", "websockets", "google-cloud-aiplatform")
$missingPackages = @()

foreach ($pkg in $requiredPackages) {
    $installed = & python -c "import $($pkg.Replace('-', '_'))" 2>&1
    if ($LASTEXITCODE -ne 0) {
        $missingPackages += $pkg
    }
}

if ($missingPackages.Count -gt 0) {
    Write-Host "⚠️  缺少套件，正在安裝..." -ForegroundColor Yellow
    foreach ($pkg in $missingPackages) {
        Write-Host "  安裝 $pkg..." -ForegroundColor Gray
        & python -m pip install $pkg --quiet
    }
    Write-Host "✅ 依賴安裝完成" -ForegroundColor Green
    Write-Host ""
}

# 選擇模式
Write-Host "請選擇運行模式:" -ForegroundColor Cyan
Write-Host "  1. 命令行互動模式（推薦測試）" -ForegroundColor White
Write-Host "  2. Streamlit Web 介面（推薦日常使用）" -ForegroundColor White
Write-Host ""

$mode = Read-Host "請輸入選項 (1/2)"

if ($mode -eq "1") {
    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "  🚀 啟動命令行互動模式..." -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host ""
    
    & python ai_ui_controller.py
}
elseif ($mode -eq "2") {
    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "  🚀 啟動 Streamlit Web 介面..." -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "瀏覽器將自動打開，或訪問: http://localhost:8501" -ForegroundColor Yellow
    Write-Host ""
    
    & streamlit run chat_app_integrated.py
}
else {
    Write-Host "❌ 無效的選項" -ForegroundColor Red
    exit 1
}
