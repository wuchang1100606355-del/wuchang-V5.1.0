# 時空系統依賴安裝腳本
# 需要管理員權限

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "時空系統依賴安裝腳本" -ForegroundColor Cyan
Write-Host "AI 小 J 完整授權模式" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 檢查管理員權限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "警告: 建議以管理員權限執行以確保完整安裝" -ForegroundColor Yellow
}

# 檢查 Python
Write-Host "`n檢查 Python 環境..." -ForegroundColor Green
try {
    $pythonVersion = python --version
    Write-Host "✓ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python 未安裝，請先安裝 Python 3.8+" -ForegroundColor Red
    exit 1
}

# 升級 pip
Write-Host "`n升級 pip..." -ForegroundColor Green
python -m pip install --upgrade pip

# 安裝依賴
Write-Host "`n安裝時空系統依賴套件..." -ForegroundColor Green
$requirementsPath = Join-Path $PSScriptRoot "..\requirements.txt"
if (Test-Path $requirementsPath) {
    python -m pip install -r $requirementsPath
    Write-Host "✓ 依賴套件安裝完成" -ForegroundColor Green
} else {
    Write-Host "✗ requirements.txt 不存在" -ForegroundColor Red
}

# 安裝 Google Calendar API 相關
Write-Host "`n安裝 Google Calendar API 套件..." -ForegroundColor Green
python -m pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
Write-Host "✓ Google Calendar API 套件安裝完成" -ForegroundColor Green

# 安裝空間計算套件
Write-Host "`n安裝空間計算套件..." -ForegroundColor Green
python -m pip install geopy shapely pyproj
Write-Host "✓ 空間計算套件安裝完成" -ForegroundColor Green

# 安裝 AI/ML 套件（雲端算力）
Write-Host "`n安裝 AI/ML 套件（雲端算力）..." -ForegroundColor Green
python -m pip install openai anthropic google-generativeai
Write-Host "✓ AI/ML 套件安裝完成" -ForegroundColor Green

# 驗證安裝
Write-Host "`n驗證安裝..." -ForegroundColor Green
python -c "import google.auth; import geopy; import flask; print('✓ 核心套件驗證通過')"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "安裝完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
