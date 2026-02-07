# Google Maps API 設定腳本
# 用途：協助設定 Google Maps API Key

param(
    [string]$ApiKey = "",
    [string]$VMIP = "192.168.50.249"
)

Write-Host "`n=== Google Maps API 設定 ===" -ForegroundColor Cyan
Write-Host ""

if (-not $ApiKey) {
    Write-Host "請提供 Google Maps API Key" -ForegroundColor Yellow
    Write-Host "`n取得 API Key 步驟：" -ForegroundColor Cyan
    Write-Host "  1. 訪問: https://console.cloud.google.com/" -ForegroundColor White
    Write-Host "  2. 選擇或建立專案" -ForegroundColor White
    Write-Host "  3. 啟用 Maps Embed API 和 Geocoding API" -ForegroundColor White
    Write-Host "  4. 建立 API Key" -ForegroundColor White
    Write-Host "  5. 複製 API Key（格式：AIza...）" -ForegroundColor White
    Write-Host "`n使用方式：" -ForegroundColor Yellow
    Write-Host "  .\scripts\setup_google_maps_api.ps1 -ApiKey ""您的 API Key""" -ForegroundColor White
    Write-Host "`n詳細指南：" -ForegroundColor Cyan
    Write-Host "  docs\GOOGLE_MAPS_API_SETUP.md" -ForegroundColor White
    exit 1
}

Write-Host "API Key: $($ApiKey.Substring(0, [Math]::Min(20, $ApiKey.Length)))..." -ForegroundColor White
Write-Host "VM 伺服器: $VMIP" -ForegroundColor White
Write-Host ""

# 驗證 API Key 格式
if (-not $ApiKey.StartsWith("AIza")) {
    Write-Host "⚠️  警告：API Key 格式可能不正確（應以 AIza 開頭）" -ForegroundColor Yellow
    $confirm = Read-Host "是否繼續？(Y/N)"
    if ($confirm -ne "Y" -and $confirm -ne "y") {
        exit 0
    }
}

Write-Host "正在設定 API Key..." -ForegroundColor Yellow

# 方式 1: 透過 Odoo API（如果可用）
try {
    $odooUrl = "http://${VMIP}:8069/web/dataset/call_kw"
    $body = @{
        model = "ir.config_parameter"
        method = "set_param"
        args = @("google.maps.api_key", $ApiKey)
        kwargs = @{}
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri $odooUrl -Method POST -Body $body -ContentType "application/json" -ErrorAction Stop
    
    Write-Host "✅ API Key 已設定到 Odoo" -ForegroundColor Green
} catch {
    Write-Host "⚠️  無法透過 API 設定，請使用手動方式：" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "手動設定步驟：" -ForegroundColor Cyan
    Write-Host "  1. 訪問: http://${VMIP}:8069/web/login" -ForegroundColor White
    Write-Host "  2. 進入「設定」→「技術」→「參數」→「系統參數」" -ForegroundColor White
    Write-Host "  3. 搜尋或建立參數：" -ForegroundColor White
    Write-Host "     參數名稱: google.maps.api_key" -ForegroundColor Gray
    Write-Host "     參數值: $ApiKey" -ForegroundColor Gray
    Write-Host "  4. 儲存設定" -ForegroundColor White
    Write-Host ""
}

Write-Host "`n驗證設定：" -ForegroundColor Cyan
Write-Host "  1. 訪問設備專屬網頁 APP" -ForegroundColor White
Write-Host "  2. 點擊「取得目前位置」" -ForegroundColor White
Write-Host "  3. 如果看到 Google Maps 地圖，表示設定成功！" -ForegroundColor White
Write-Host ""
Write-Host "詳細指南：" -ForegroundColor Cyan
Write-Host "  docs\GOOGLE_MAPS_API_SETUP.md" -ForegroundColor White
