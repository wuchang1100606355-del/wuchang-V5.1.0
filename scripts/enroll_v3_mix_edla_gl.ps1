# Android POS 設備納管腳本 - v3_mix_edla_gl
# 設備資訊：
#   - 設備名稱: v3_mix_edla_gl
#   - Android 版本: 13
#   - IP 地址: 192.168.50.86
#   - 通訊埠: 41895
#   - 開發者模式: 已開啟
#   - 偵錯選項: USB、GPU、WiFi 已開啟

param(
    [string]$VMIP = "192.168.50.249",  # VM 為本地機器
    [string]$DeviceIP = "192.168.50.86",
    [int]$DevicePort = 41895,
    [string]$DeviceName = "v3_mix_edla_gl",
    [string]$AndroidVersion = "13"
)

$EnrollmentURL = "http://${VMIP}:8069/api/device/enroll/android"

Write-Host "`n=== Android POS 設備納管 ===" -ForegroundColor Cyan
Write-Host "設備名稱: $DeviceName" -ForegroundColor White
Write-Host "Android 版本: $AndroidVersion" -ForegroundColor White
Write-Host "IP 地址: $DeviceIP" -ForegroundColor White
Write-Host "通訊埠: $DevicePort" -ForegroundColor White
Write-Host "VM 伺服器: $VMIP" -ForegroundColor White
Write-Host ""

# 準備納管資料
    $enrollmentData = @{
        device_id = "ANDROID_V3_MIX_EDLA_GL"
        device_name = $DeviceName
        device_type = "pos"
        os_type = "android"
        os_version = $AndroidVersion
        ip_address = $DeviceIP
        port = $DevicePort
        developer_mode = $true
        demo_mode = $false
        is_primary = $true  # 標記為主要 POS 設備
    debug_options = @{
        usb = $true
        gpu = $true
        wifi = $true
    }
    capabilities = @{
        kiosk_mode = $true
        remote_management = $true
        app_deployment = $true
        data_sync = $true
    }
    anydesk_id = "748464958"  # AnyDesk ID
    anydesk_configured = $false  # AnyDesk 設定狀態：未完成
    note = "主要 POS 設備（v3_mix_edla_gl），原 POS 設備即將汰換，AnyDesk ID: 748464958（設定未完成）"
} | ConvertTo-Json -Depth 10

Write-Host "正在納管設備..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri $EnrollmentURL -Method POST -Body $enrollmentData -ContentType "application/json" -TimeoutSec 10
    
    if ($response.status -eq 'success') {
        Write-Host "`n✅ 設備納管成功！" -ForegroundColor Green
        Write-Host "`n設備資訊：" -ForegroundColor Cyan
        Write-Host "  設備 ID: $($response.device.device_id)" -ForegroundColor White
        Write-Host "  設備名稱: $($response.device.name)" -ForegroundColor White
        Write-Host "  IP 地址: $($response.device.ip_address)" -ForegroundColor White
        Write-Host "  通訊埠: $($response.device.port)" -ForegroundColor White
        Write-Host "  狀態: $($response.device.status)" -ForegroundColor White
        Write-Host "  開發者模式: $($response.device.developer_mode)" -ForegroundColor White
        Write-Host "  Demo Mode: $($response.device.demo_mode)" -ForegroundColor White
        
        Write-Host "`n偵錯選項：" -ForegroundColor Cyan
        Write-Host "  USB 偵錯: $($response.device.debug_options.usb)" -ForegroundColor White
        Write-Host "  GPU 偵錯: $($response.device.debug_options.gpu)" -ForegroundColor White
        Write-Host "  WiFi 偵錯: $($response.device.debug_options.wifi)" -ForegroundColor White
        
        Write-Host "`n建議：" -ForegroundColor Yellow
        if ($response.recommendations) {
            Write-Host "  Demo Mode: $($response.recommendations.demo_mode.reason)" -ForegroundColor White
            Write-Host "  替代方案: $($response.recommendations.demo_mode.alternative)" -ForegroundColor White
        }
        
        Write-Host "`n下一步：" -ForegroundColor Yellow
        Write-Host "  1. 在 Google Workspace Admin Console 註冊此設備" -ForegroundColor White
        Write-Host "  2. 設定 Kiosk 模式（鎖定到 Odoo POS 應用）" -ForegroundColor White
        Write-Host "  3. 配置 Google Drive 同步" -ForegroundColor White
        Write-Host "  4. 測試設備連線和功能" -ForegroundColor White
        
        Write-Host "`n訪問連結：" -ForegroundColor Cyan
        Write-Host "  設備管理: http://${VMIP}:8069$($response.access.device_management)" -ForegroundColor White
        Write-Host "  Sister Control: http://${VMIP}:8069$($response.access.sister_control)" -ForegroundColor White
        
        return 0
    } else {
        Write-Host "`n❌ 納管失敗: $($response.message)" -ForegroundColor Red
        return 1
    }
} catch {
    Write-Host "`n❌ 納管失敗: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`n請確認：" -ForegroundColor Yellow
    Write-Host "  1. VM 伺服器的 Odoo 服務正在運行" -ForegroundColor White
    Write-Host "  2. 網路連線正常" -ForegroundColor White
    Write-Host "  3. IP 地址正確 ($VMIP)" -ForegroundColor White
    Write-Host "  4. 防火牆未阻擋連線" -ForegroundColor White
    return 1
}
