# v3_mix_edla_gl Android POS 設備納管腳本（使用本機 Odoo 服務）
# 用途：當 VM 伺服器無法訪問時，使用本機 Odoo 服務進行納管

$VMIP = "192.168.50.249"  # VM 為本地機器
$DeviceName = "v3_mix_edla_gl"
$AndroidVersion = "13"
$DeviceIP = "192.168.50.86"
$DevicePort = 41895
$EnrollmentUrl = "http://${VMIP}:8069/api/device/enroll/android"

Write-Host ""
Write-Host "=== Android POS 設備納管 ===" -ForegroundColor Cyan
Write-Host "設備名稱: $DeviceName" -ForegroundColor White
Write-Host "Android 版本: $AndroidVersion" -ForegroundColor White
Write-Host "IP 地址: $DeviceIP" -ForegroundColor White
Write-Host "通訊埠: $DevicePort" -ForegroundColor White
Write-Host "VM 伺服器: $VMIP (本機 Odoo 服務)" -ForegroundColor White
Write-Host ""

# 檢查 Odoo 服務是否可訪問
Write-Host "檢查 Odoo 服務..." -ForegroundColor Yellow
try {
    $testConnection = Test-NetConnection -ComputerName localhost -Port 8069 -InformationLevel Quiet -WarningAction SilentlyContinue -ErrorAction Stop
    if ($testConnection) {
        Write-Host "  ✅ Odoo 服務可訪問" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Odoo 服務無法訪問" -ForegroundColor Red
        Write-Host ""
        Write-Host "請確認：" -ForegroundColor Yellow
        Write-Host "  1. Odoo 服務正在運行" -ForegroundColor White
        Write-Host "  2. 端口 8069 已開放" -ForegroundColor White
        exit 1
    }
} catch {
    Write-Host "  ❌ 無法檢查 Odoo 服務: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "正在納管設備..." -ForegroundColor Yellow

# 準備納管資料
$enrollmentData = @{
    device_id = "ANDROID_$($DeviceName.ToUpper().Replace(' ', '_'))"
    device_name = $DeviceName
    device_type = "pos"
    os_type = "android"
    os_version = $AndroidVersion
    ip_address = $DeviceIP
    port = $DevicePort
    mac_address = ""  # 可選
    developer_mode = $true
    demo_mode = $false
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
    enrollment_time = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    managed_by = "Little J (小j)"
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-RestMethod -Uri $EnrollmentUrl -Method Post -Body $enrollmentData -ContentType "application/json" -TimeoutSec 10
    
    Write-Host ""
    Write-Host "✅ 設備納管成功！" -ForegroundColor Green
    Write-Host "   設備 ID: $($response.device.id)" -ForegroundColor White
    Write-Host "   狀態: $($response.status)" -ForegroundColor White
    Write-Host ""
    Write-Host "下一步：" -ForegroundColor Cyan
    Write-Host "  1. 在 Odoo 中確認設備記錄" -ForegroundColor White
    Write-Host "  2. 在 Google Workspace Admin Console 註冊設備" -ForegroundColor White
    Write-Host "  3. 設定 Kiosk 模式和應用程式政策" -ForegroundColor White
    
} catch {
    Write-Host ""
    Write-Host "❌ 納管失敗: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "請確認：" -ForegroundColor Yellow
    Write-Host "  1. Odoo 服務正在運行" -ForegroundColor White
    Write-Host "  2. API 端點正確: $EnrollmentUrl" -ForegroundColor White
    Write-Host "  3. 網路連線正常" -ForegroundColor White
    Write-Host ""
    Write-Host "替代方案：" -ForegroundColor Yellow
    Write-Host "  • 透過 Odoo UI 手動納管（見 scripts\enroll_device_odoo_ui.md）" -ForegroundColor White
    Write-Host "  • 使用 SQL 直接納管（見 scripts\enroll_v3_mix_edla_gl_sql.sql）" -ForegroundColor White
    exit 1
}
