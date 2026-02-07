# 與 UI 設備溝通腳本
# 用於與 UI 筆電進行通信和指令傳送

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("sync", "reload", "status", "command")]
    [string]$Action = "status",
    
    [Parameter(Mandatory=$false)]
    [string]$DeviceIP = "192.168.50.84",
    
    [Parameter(Mandatory=$false)]
    [string]$Command = "",
    
    [Parameter(Mandatory=$false)]
    [string]$OdooURL = "http://localhost:8069"
)

Write-Host "=== 與 UI 設備溝通 ===" -ForegroundColor Cyan

# 1. 檢查 Odoo 服務
Write-Host "`n[1] 檢查 Odoo 服務..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$OdooURL/web/login" -Method GET -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  ✓ Odoo 服務在線: $OdooURL" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Odoo 服務可能離線: $OdooURL" -ForegroundColor Yellow
    Write-Host "    錯誤: $($_.Exception.Message)" -ForegroundColor Gray
}

# 2. 檢查設備連接性
Write-Host "`n[2] 檢查設備連接性..." -ForegroundColor Yellow
try {
    $result = Test-Connection -ComputerName $DeviceIP -Count 1 -Quiet -ErrorAction SilentlyContinue
    if ($result) {
        Write-Host "  ✓ 設備在線: $DeviceIP" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ 設備可能離線: $DeviceIP" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ⚠ 無法檢查設備連接性" -ForegroundColor Yellow
}

# 3. 根據動作執行
Write-Host "`n[3] 執行動作: $Action" -ForegroundColor Yellow

switch ($Action) {
    "status" {
        Write-Host "  查詢設備狀態..." -ForegroundColor Cyan
        Write-Host "`n  可用的溝通方式：" -ForegroundColor Yellow
        Write-Host "    1. Odoo API: $OdooURL/wuchang/sister/poll" -ForegroundColor White
        Write-Host "    2. 設備 IP: $DeviceIP" -ForegroundColor White
        Write-Host "    3. 使用 Python 腳本: python scripts/notify_ui_devices.py" -ForegroundColor White
        Write-Host "    4. 使用 Odoo 後台: $OdooURL/web#id=1&model=wuchang.sister.control" -ForegroundColor White
    }
    
    "sync" {
        Write-Host "  發送同步指令..." -ForegroundColor Cyan
        
        # 嘗試通過 Odoo API 發送指令
        $apiUrl = "$OdooURL/wuchang/sister/poll"
        Write-Host "  使用 API: $apiUrl" -ForegroundColor Gray
        
        # 這裡應該使用 Odoo 的 API 發送指令
        # 需要先登入 Odoo 獲取 session
        Write-Host "  提示: 請使用 Odoo 後台發送同步指令" -ForegroundColor Yellow
        Write-Host "  或使用 Python 腳本: python scripts/notify_ui_devices.py" -ForegroundColor Cyan
    }
    
    "reload" {
        Write-Host "  發送重新載入指令..." -ForegroundColor Cyan
        Write-Host "  提示: 請使用 Odoo 後台發送重新載入指令" -ForegroundColor Yellow
        Write-Host "  或使用 Python 腳本: python scripts/notify_ui_devices.py" -ForegroundColor Cyan
    }
    
    "command" {
        if ($Command) {
            Write-Host "  發送自訂指令: $Command" -ForegroundColor Cyan
            Write-Host "  提示: 請使用 Odoo 後台發送自訂指令" -ForegroundColor Yellow
        } else {
            Write-Host "  ⚠ 未指定指令內容" -ForegroundColor Yellow
            Write-Host "  使用方式: .\scripts\communicate_with_ui.ps1 -Action command -Command 'your_command'" -ForegroundColor Cyan
        }
    }
}

# 4. 顯示可用的溝通方式
Write-Host "`n[4] 可用的溝通方式：" -ForegroundColor Yellow

Write-Host "`n  方式 1: 使用 Odoo 後台（推薦）" -ForegroundColor Cyan
Write-Host "    1. 開啟: $OdooURL/web#id=1&model=wuchang.sister.control" -ForegroundColor White
Write-Host "    2. 點擊「同步 POS」或「同步客顯」按鈕" -ForegroundColor White
Write-Host "    3. UI 設備會自動接收指令" -ForegroundColor White

Write-Host "`n  方式 2: 使用 Python 腳本" -ForegroundColor Cyan
Write-Host "    python scripts/notify_ui_devices.py" -ForegroundColor White

Write-Host "`n  方式 3: 使用 API 直接調用" -ForegroundColor Cyan
Write-Host "    API 端點: $OdooURL/wuchang/sister/poll" -ForegroundColor White
Write-Host "    方法: POST" -ForegroundColor White
Write-Host "    參數: device_type=POS 或 device_type=CUSTOMER" -ForegroundColor White

Write-Host "`n  方式 4: 使用 sister_agent.py（在 UI 設備上）" -ForegroundColor Cyan
Write-Host "    在 UI 設備上執行: python sister_agent.py --device POS" -ForegroundColor White
Write-Host "    或: python sister_agent.py --device CUSTOMER" -ForegroundColor White

Write-Host "`n=== 完成 ===" -ForegroundColor Cyan
