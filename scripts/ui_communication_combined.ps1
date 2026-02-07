# UI 設備溝通整合方案（方式 3 + 方式 4）
# 結合 API 直接調用和 Sister Agent 的完整解決方案

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("sync_pos", "sync_customer", "reload", "status", "start_agent")]
    [string]$Action = "status",
    
    [Parameter(Mandatory=$false)]
    [string]$OdooURL = "http://localhost:8069",
    
    [Parameter(Mandatory=$false)]
    [string]$DeviceIP = "192.168.50.84",
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("POS", "CUSTOMER")]
    [string]$DeviceType = "POS"
)

Write-Host "=== UI 設備溝通整合方案（方式 3 + 方式 4） ===" -ForegroundColor Cyan

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
        
        # 通過 API 查詢狀態
        Write-Host "`n  [方式 3] 通過 API 查詢狀態..." -ForegroundColor Yellow
        $apiUrl = "$OdooURL/wuchang/sister/poll"
        
        try {
            $body = @{
                device_type = $DeviceType
            } | ConvertTo-Json
            
            $response = Invoke-RestMethod -Uri $apiUrl -Method POST -Body $body -ContentType "application/json" -TimeoutSec 5
            Write-Host "  ✓ API 回應成功" -ForegroundColor Green
            Write-Host "    指令數量: $($response.commands.Count)" -ForegroundColor Cyan
            Write-Host "    POS URL: $($response.config.pos_url)" -ForegroundColor Cyan
            Write-Host "    客顯 URL: $($response.config.customer_url)" -ForegroundColor Cyan
        } catch {
            Write-Host "  ⚠ API 查詢失敗: $($_.Exception.Message)" -ForegroundColor Yellow
        }
        
        # 檢查 Sister Agent 是否運行
        Write-Host "`n  [方式 4] 檢查 Sister Agent..." -ForegroundColor Yellow
        Write-Host "    在 UI 設備上執行: python sister_agent.py --device $DeviceType" -ForegroundColor Cyan
        Write-Host "    或檢查進程: Get-Process python -ErrorAction SilentlyContinue | Where-Object {`$_.CommandLine -like '*sister_agent*'}" -ForegroundColor Gray
    }
    
    "sync_pos" {
        Write-Host "  發送同步 POS 指令..." -ForegroundColor Cyan
        
        Write-Host "`n  [方式 3] 通過 API 發送指令..." -ForegroundColor Yellow
        Write-Host "    提示: 請使用 Odoo 後台或 Python 腳本發送指令" -ForegroundColor Cyan
        Write-Host "    Odoo 後台: $OdooURL/web#id=1&model=wuchang.sister.control" -ForegroundColor White
        
        Write-Host "`n  [方式 4] Sister Agent 會自動接收..." -ForegroundColor Yellow
        Write-Host "    確保在 UI 設備上運行: python sister_agent.py --device POS" -ForegroundColor Cyan
    }
    
    "sync_customer" {
        Write-Host "  發送同步客顯指令..." -ForegroundColor Cyan
        
        Write-Host "`n  [方式 3] 通過 API 發送指令..." -ForegroundColor Yellow
        Write-Host "    提示: 請使用 Odoo 後台或 Python 腳本發送指令" -ForegroundColor Cyan
        Write-Host "    Odoo 後台: $OdooURL/web#id=1&model=wuchang.sister.control" -ForegroundColor White
        
        Write-Host "`n  [方式 4] Sister Agent 會自動接收..." -ForegroundColor Yellow
        Write-Host "    確保在 UI 設備上運行: python sister_agent.py --device CUSTOMER" -ForegroundColor Cyan
    }
    
    "reload" {
        Write-Host "  發送重新載入指令..." -ForegroundColor Cyan
        Write-Host "    提示: 請使用 Odoo 後台發送重新載入指令" -ForegroundColor Yellow
        Write-Host "    或確保 Sister Agent 正在運行以接收指令" -ForegroundColor Cyan
    }
    
    "start_agent" {
        Write-Host "  啟動 Sister Agent（需要在 UI 設備上執行）..." -ForegroundColor Cyan
        Write-Host "`n  [方式 4] 啟動 Sister Agent..." -ForegroundColor Yellow
        
        if (Test-Path "sister_agent.py") {
            Write-Host "  ✓ 找到 sister_agent.py" -ForegroundColor Green
            Write-Host "`n  執行命令: python sister_agent.py --device $DeviceType" -ForegroundColor Cyan
            
            $startAgent = Read-Host "  是否要現在啟動？ (Y/N)"
            if ($startAgent -eq 'Y' -or $startAgent -eq 'y') {
                Write-Host "`n  正在啟動 Sister Agent..." -ForegroundColor Yellow
                Start-Process python -ArgumentList "sister_agent.py", "--device", $DeviceType -NoNewWindow
                Write-Host "  ✓ Sister Agent 已啟動" -ForegroundColor Green
            } else {
                Write-Host "  已取消啟動" -ForegroundColor Gray
            }
        } else {
            Write-Host "  ⚠ 未找到 sister_agent.py" -ForegroundColor Yellow
            Write-Host "    請確認檔案存在於當前目錄" -ForegroundColor Cyan
        }
    }
}

# 4. 顯示整合方案說明
Write-Host "`n[4] 整合方案說明..." -ForegroundColor Yellow
Write-Host "`n  方式 3 + 方式 4 的整合使用：" -ForegroundColor Cyan
Write-Host "    1. 在 UI 設備上運行 Sister Agent（方式 4）" -ForegroundColor White
Write-Host "       python sister_agent.py --device POS" -ForegroundColor Gray
Write-Host "`n    2. 通過 API 或 Odoo 後台發送指令（方式 3）" -ForegroundColor White
Write-Host "       方式 3A: Odoo 後台（推薦）" -ForegroundColor Gray
Write-Host "         $OdooURL/web#id=1&model=wuchang.sister.control" -ForegroundColor Gray
Write-Host "       方式 3B: API 直接調用" -ForegroundColor Gray
Write-Host "         POST $OdooURL/wuchang/sister/poll" -ForegroundColor Gray
Write-Host "`n    3. Sister Agent 會自動輪詢接收指令（方式 4）" -ForegroundColor White
Write-Host "`n    4. 指令執行完成" -ForegroundColor White

Write-Host "`n=== 完成 ===" -ForegroundColor Cyan
