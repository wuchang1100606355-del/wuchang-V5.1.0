# POS 設備 AnyDesk 設定腳本
# 用途：為 v3_mix_edla_gl 設定 AnyDesk 遠程桌面

param(
    [string]$VMIP = "192.168.50.249",
    [string]$DeviceName = "v3_mix_edla_gl",
    [string]$AnyDeskID = "748464958",
    [string]$AnyDeskPassword = "",
    [switch]$Configured = $false
)

Write-Host "`n=== POS 設備 AnyDesk 設定 ===" -ForegroundColor Cyan
Write-Host "設備: $DeviceName" -ForegroundColor White
Write-Host "AnyDesk ID: $AnyDeskID" -ForegroundColor White
Write-Host "設定狀態: $(if ($Configured) { '已完成' } else { '未完成' })" -ForegroundColor $(if ($Configured) { 'Green' } else { 'Yellow' })
Write-Host ""

$enrollmentData = @{
    device_name = $DeviceName
    ip_address = "192.168.50.86"
    port = 41895
    os_version = "13"
    developer_mode = $true
    anydesk_id = $AnyDeskID
    anydesk_configured = $Configured
    debug_options = @{
        usb = $true
        gpu = $true
        wifi = $true
    }
} | ConvertTo-Json -Depth 10

if ($AnyDeskPassword) {
    $enrollmentDataObj = $enrollmentData | ConvertFrom-Json
    $enrollmentDataObj | Add-Member -MemberType NoteProperty -Name "anydesk_password" -Value $AnyDeskPassword
    $enrollmentData = $enrollmentDataObj | ConvertTo-Json -Depth 10
}

Write-Host "正在更新 AnyDesk 設定..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "http://${VMIP}:8069/api/device/enroll/android" -Method POST -Body $enrollmentData -ContentType "application/json" -TimeoutSec 10
    
    if ($response.status -eq 'success') {
        Write-Host "`n✅ AnyDesk 設定已更新！" -ForegroundColor Green
        Write-Host "`n設備資訊：" -ForegroundColor Cyan
        Write-Host "  設備名稱: $($response.device.name)" -ForegroundColor White
        Write-Host "  AnyDesk ID: $($response.device.anydesk_id)" -ForegroundColor White
        Write-Host "  設定狀態: $(if ($response.device.anydesk_configured) { '已完成' } else { '未完成' })" -ForegroundColor $(if ($response.device.anydesk_configured) { 'Green' } else { 'Yellow' })
        
        Write-Host "`n下一步：" -ForegroundColor Yellow
        Write-Host "  1. 在 v3_mix_edla_gl 設備上完成 AnyDesk 設定" -ForegroundColor White
        Write-Host "  2. 測試遠程連線（AnyDesk ID: $AnyDeskID）" -ForegroundColor White
        Write-Host "  3. 設定完成後，執行以下命令標記為已完成：" -ForegroundColor White
        Write-Host "     .\scripts\configure_anydesk_pos.ps1 -Configured" -ForegroundColor Gray
        
        return 0
    } else {
        Write-Host "`n❌ 更新失敗: $($response.message)" -ForegroundColor Red
        return 1
    }
} catch {
    Write-Host "`n❌ 更新失敗: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`n請確認：" -ForegroundColor Yellow
    Write-Host "  1. VM 伺服器的 Odoo 服務正在運行" -ForegroundColor White
    Write-Host "  2. 網路連線正常" -ForegroundColor White
    Write-Host "  3. IP 地址正確 ($VMIP)" -ForegroundColor White
    return 1
}
