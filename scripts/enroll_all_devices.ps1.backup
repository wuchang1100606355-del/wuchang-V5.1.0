# 批量納管所有設備腳本
# 用途：納管客戶顯示器和 Chrome OS 設備

param(
    [string]$VMIP = "192.168.50.249",
    [string]$CustomerDisplayIP = "",
    [string]$CustomerDisplayName = "Customer Display",
    [string]$ChromeOSDevicesFile = "chrome_os_devices.json"
)

Write-Host "`n=== 批量設備納管 ===" -ForegroundColor Cyan
Write-Host "VM 伺服器: $VMIP" -ForegroundColor White
Write-Host ""

# 1. 納管客戶顯示器
if ($CustomerDisplayIP) {
    Write-Host "[1] 納管客戶顯示器..." -ForegroundColor Yellow
    Write-Host "  IP: $CustomerDisplayIP" -ForegroundColor White
    Write-Host "  名稱: $CustomerDisplayName" -ForegroundColor White
    
    python scripts\enroll_customer_display.py `
        --device-name "$CustomerDisplayName" `
        --ip "$CustomerDisplayIP" `
        --display-url "http://$VMIP:8069/pos/customer_display" `
        --vm-ip "$VMIP"
    
    Write-Host ""
}

# 2. 批量納管 Chrome OS 設備
if (Test-Path $ChromeOSDevicesFile) {
    Write-Host "[2] 批量納管 Chrome OS 設備..." -ForegroundColor Yellow
    Write-Host "  設備清單: $ChromeOSDevicesFile" -ForegroundColor White
    
    python scripts\batch_enroll_chrome_os_devices.py `
        --devices-file "$ChromeOSDevicesFile" `
        --vm-ip "$VMIP"
    
    Write-Host ""
} else {
    Write-Host "[2] Chrome OS 設備清單不存在: $ChromeOSDevicesFile" -ForegroundColor Yellow
    Write-Host "  建立範本: python scripts\batch_enroll_chrome_os_devices.py --create-template" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "=== 納管完成 ===" -ForegroundColor Green
Write-Host "`n下一步：" -ForegroundColor Cyan
Write-Host "  1. 在 Odoo 中確認所有設備記錄" -ForegroundColor White
Write-Host "  2. 在 Sister Control 中配置設備 URL" -ForegroundColor White
Write-Host "  3. 測試設備連線和功能" -ForegroundColor White
