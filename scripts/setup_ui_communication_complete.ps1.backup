# 設定完整的 UI 溝通方案（方式 3 + 方式 4）
# 自動設定 API 端點和 Sister Agent

Write-Host "=== 設定完整的 UI 溝通方案（方式 3 + 方式 4） ===" -ForegroundColor Cyan

# 1. 檢查並建立必要的檔案
Write-Host "`n[1] 檢查必要檔案..." -ForegroundColor Yellow

$requiredFiles = @(
    "sister_agent.py",
    "scripts\communicate_with_ui.ps1",
    "scripts\ui_communication_combined.ps1"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ $file 不存在" -ForegroundColor Yellow
    }
}

# 2. 設定 API 端點資訊
Write-Host "`n[2] 設定 API 端點資訊..." -ForegroundColor Yellow

$odooURL = "http://localhost:8069"
$apiEndpoint = "$odooURL/wuchang/sister/poll"

Write-Host "  Odoo URL: $odooURL" -ForegroundColor Cyan
Write-Host "  API 端點: $apiEndpoint" -ForegroundColor Cyan
Write-Host "  方法: POST" -ForegroundColor Cyan
Write-Host "  Content-Type: application/json" -ForegroundColor Cyan

# 3. 測試 API 連接
Write-Host "`n[3] 測試 API 連接..." -ForegroundColor Yellow

try {
    $body = @{
        device_type = "POS"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri $apiEndpoint -Method POST -Body $body -ContentType "application/json" -TimeoutSec 5
    Write-Host "  ✓ API 連接成功" -ForegroundColor Green
    Write-Host "    回應: 指令數量 = $($response.commands.Count)" -ForegroundColor Cyan
} catch {
    Write-Host "  ⚠ API 連接失敗: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "    提示: 確保 Odoo 服務正在運行" -ForegroundColor Cyan
}

# 4. 檢查 Sister Agent 設定
Write-Host "`n[4] 檢查 Sister Agent 設定..." -ForegroundColor Yellow

if (Test-Path "sister_agent.py") {
    Write-Host "  ✓ sister_agent.py 存在" -ForegroundColor Green
    
    # 讀取檔案查看配置
    $content = Get-Content "sister_agent.py" -Raw
    if ($content -match "VM_URL\s*=\s*['""]([^'""]+)['""]") {
        $vmUrl = $matches[1]
        Write-Host "  VM URL: $vmUrl" -ForegroundColor Cyan
    }
    
    Write-Host "`n  使用方式（在 UI 設備上執行）：" -ForegroundColor Yellow
    Write-Host "    python sister_agent.py --device POS" -ForegroundColor White
    Write-Host "    python sister_agent.py --device CUSTOMER" -ForegroundColor White
} else {
    Write-Host "  ⚠ sister_agent.py 不存在" -ForegroundColor Yellow
}

# 5. 建立快速啟動腳本
Write-Host "`n[5] 建立快速啟動腳本..." -ForegroundColor Yellow

$startAgentScript = @"
# 快速啟動 Sister Agent
# 使用方式: .\start_sister_agent.ps1 -Device POS

param(
    [Parameter(Mandatory=`$false)]
    [ValidateSet("POS", "CUSTOMER")]
    [string]`$Device = "POS"
)

Write-Host "啟動 Sister Agent - `$Device" -ForegroundColor Cyan
python sister_agent.py --device `$Device
"@

$startScriptPath = "start_sister_agent.ps1"
if (-not (Test-Path $startScriptPath)) {
    Set-Content -Path $startScriptPath -Value $startAgentScript
    Write-Host "  ✓ 已建立: $startScriptPath" -ForegroundColor Green
} else {
    Write-Host "  ✓ 已存在: $startScriptPath" -ForegroundColor Green
}

# 6. 顯示整合使用指南
Write-Host "`n[6] 整合使用指南..." -ForegroundColor Yellow

Write-Host "`n=== 方式 3 + 方式 4 整合使用 ===" -ForegroundColor Cyan
Write-Host "`n步驟 1: 在 UI 設備上啟動 Sister Agent（方式 4）" -ForegroundColor Yellow
Write-Host "  .\start_sister_agent.ps1 -Device POS" -ForegroundColor White
Write-Host "  或" -ForegroundColor Gray
Write-Host "  python sister_agent.py --device POS" -ForegroundColor White

Write-Host "`n步驟 2: 通過 API 或 Odoo 後台發送指令（方式 3）" -ForegroundColor Yellow
Write-Host "  方式 3A: Odoo 後台（推薦）" -ForegroundColor Cyan
Write-Host "    $odooURL/web#id=1&model=wuchang.sister.control" -ForegroundColor White
Write-Host "    點擊「同步 POS」或「同步客顯」按鈕" -ForegroundColor Gray
Write-Host "`n  方式 3B: 使用 PowerShell 腳本" -ForegroundColor Cyan
Write-Host "    .\scripts\ui_communication_combined.ps1 -Action sync_pos" -ForegroundColor White
Write-Host "`n  方式 3C: API 直接調用" -ForegroundColor Cyan
Write-Host "    POST $apiEndpoint" -ForegroundColor White
Write-Host "    Body: {`"device_type`": `"POS`"}" -ForegroundColor Gray

Write-Host "`n步驟 3: Sister Agent 自動接收並執行指令（方式 4）" -ForegroundColor Yellow
Write-Host "  - Agent 每 5 秒輪詢一次 API" -ForegroundColor White
Write-Host "  - 接收到指令後自動執行" -ForegroundColor White
Write-Host "  - 執行結果會顯示在 Agent 輸出中" -ForegroundColor White

Write-Host "`n=== 完成 ===" -ForegroundColor Green
