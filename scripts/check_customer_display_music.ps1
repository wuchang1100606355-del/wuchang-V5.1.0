# 客顯設備音樂播放檢查腳本
# 檢查客顯設備是否播放台灣地區咖啡館常用音樂

Param(
    [string]$DeviceIP = "",
    [int]$DeviceID = 0,
    [string]$VMIP = "192.168.50.249",
    [int]$Port = 8069
)

Write-Host "`n=== 客顯設備音樂播放檢查 ===" -ForegroundColor Cyan
Write-Host "VM 伺服器: $VMIP:$Port" -ForegroundColor White
Write-Host ""

$OdooURL = "http://${VMIP}:${Port}"

# 1. 如果提供了設備 IP，嘗試查詢設備 ID
if ($DeviceIP -and -not $DeviceID) {
    Write-Host "[1] 查詢設備 ID..." -ForegroundColor Yellow
    try {
        $queryUrl = "${OdooURL}/api/device/query?ip_address=$DeviceIP"
        $deviceInfo = Invoke-RestMethod -Uri $queryUrl -Method GET -TimeoutSec 5 -ErrorAction Stop
        if ($deviceInfo.status -eq 'success' -and $deviceInfo.device) {
            $DeviceID = $deviceInfo.device.id
            Write-Host "  ✓ 找到設備 ID: $DeviceID" -ForegroundColor Green
        } else {
            Write-Host "  ❌ 無法找到設備" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "  ❌ 查詢設備失敗: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

if (-not $DeviceID) {
    Write-Host "❌ 請提供設備 IP 或設備 ID" -ForegroundColor Red
    Write-Host "用法: .\check_customer_display_music.ps1 -DeviceIP '192.168.50.XXX' 或 -DeviceID 123" -ForegroundColor Yellow
    exit 1
}

# 2. 獲取設備的音樂設定
Write-Host "`n[2] 獲取設備音樂設定..." -ForegroundColor Yellow
try {
    $configUrl = "${OdooURL}/api/customer_display/music/config?device_id=$DeviceID"
    $config = Invoke-RestMethod -Uri $configUrl -Method GET -TimeoutSec 5 -ErrorAction Stop
    
    if ($config.status -eq 'success') {
        Write-Host "  ✓ 設定類型: $($config.config.config_type)" -ForegroundColor Green
        Write-Host "  ✓ 優先級: $($config.config.priority)" -ForegroundColor Green
        Write-Host "  ✓ 狀態: $($config.message)" -ForegroundColor Green
        
        if ($config.config.playlist -and $config.config.playlist.Count -gt 0) {
            Write-Host "`n  播放清單：" -ForegroundColor Cyan
            foreach ($item in $config.config.playlist) {
                Write-Host "    - $($item.name) - $($item.artist) ($($item.genre))" -ForegroundColor White
            }
        }
    } elseif ($config.status -eq 'no_config') {
        Write-Host "  ⚠ 設備未設定音樂播放配置" -ForegroundColor Yellow
        Write-Host "  建議：在 Odoo 後台為設備設定音樂配置（人為設定優先）" -ForegroundColor Yellow
    } else {
        Write-Host "  ❌ 獲取設定失敗: $($config.message)" -ForegroundColor Red
    }
} catch {
    Write-Host "  ❌ 獲取設定失敗: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. 模擬設備端回報音樂播放狀態（需要實際的音樂資訊）
Write-Host "`n[3] 檢查音樂播放狀態..." -ForegroundColor Yellow
Write-Host "  💡 提示：此檢查需要設備端實際回報音樂播放狀態" -ForegroundColor Cyan
Write-Host "  設備端應定期調用 API: POST /api/customer_display/music/check" -ForegroundColor White
Write-Host ""

# 4. 獲取符合度報告
Write-Host "[4] 獲取符合度報告（最近 7 天）..." -ForegroundColor Yellow
try {
    $reportUrl = "${OdooURL}/api/customer_display/music/compliance?device_id=$DeviceID&days=7"
    $report = Invoke-RestMethod -Uri $reportUrl -Method GET -TimeoutSec 5 -ErrorAction Stop
    
    if ($report.status -eq 'success') {
        $r = $report.report
        Write-Host "  ✓ 總檢查次數: $($r.total_checks)" -ForegroundColor Green
        Write-Host "  ✓ 符合人為設定: $($r.manual_config_matched)" -ForegroundColor Green
        Write-Host "  ✓ 不符合人為設定: $($r.manual_config_not_matched)" -ForegroundColor $(if ($r.manual_config_not_matched -gt 0) { "Yellow" } else { "Green" })
        Write-Host "  ✓ 無手動設定: $($r.no_manual_config)" -ForegroundColor White
        Write-Host "  ✓ 符合率: $([math]::Round($r.compliance_rate, 1))%" -ForegroundColor $(if ($r.compliance_rate -ge 90) { "Green" } elseif ($r.compliance_rate -ge 70) { "Yellow" } else { "Red" })
        Write-Host "  ✓ $($r.message)" -ForegroundColor White
    } else {
        Write-Host "  ❌ 獲取報告失敗: $($report.message)" -ForegroundColor Red
    }
} catch {
    Write-Host "  ❌ 獲取報告失敗: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== 檢查完成 ===" -ForegroundColor Cyan
Write-Host "`n建議：" -ForegroundColor Yellow
Write-Host "1. 在 Odoo 後台為設備設定音樂配置（基礎設施 → 客顯音樂管理 → 設備音樂設定）" -ForegroundColor White
Write-Host "2. 選擇「手動指定播放清單」並選擇適合台灣咖啡館的音樂" -ForegroundColor White
Write-Host "3. 設定優先級為 10（最高）" -ForegroundColor White
Write-Host "4. 點擊「套用設定」" -ForegroundColor White
Write-Host "5. 確認設備端可以回報音樂播放狀態" -ForegroundColor White
Write-Host ""
