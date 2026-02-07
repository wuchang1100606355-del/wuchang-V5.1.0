# 標記原 POS 設備為即將汰換
# 用途：將舊的 POS 設備標記為即將汰換，v3_mix_edla_gl 為主要 POS

param(
    [string]$VMIP = "192.168.50.249",
    [string]$OldPOSIP = "",
    [string]$OldPOSName = ""
)

Write-Host "`n=== 標記原 POS 設備為即將汰換 ===" -ForegroundColor Cyan
Write-Host "VM 伺服器: $VMIP" -ForegroundColor White
Write-Host ""

if (-not $OldPOSIP -and -not $OldPOSName) {
    Write-Host "❌ 請提供原 POS 設備的 IP 或名稱" -ForegroundColor Red
    Write-Host "`n使用方式：" -ForegroundColor Yellow
    Write-Host "  .\scripts\mark_old_pos_deprecated.ps1 -OldPOSIP ""192.168.50.XXX""" -ForegroundColor White
    Write-Host "  或" -ForegroundColor White
    Write-Host "  .\scripts\mark_old_pos_deprecated.ps1 -OldPOSName ""Old POS Device""" -ForegroundColor White
    exit 1
}

Write-Host "原 POS 設備資訊：" -ForegroundColor Yellow
if ($OldPOSIP) {
    Write-Host "  IP: $OldPOSIP" -ForegroundColor White
}
if ($OldPOSName) {
    Write-Host "  名稱: $OldPOSName" -ForegroundColor White
}
Write-Host ""

Write-Host "說明：" -ForegroundColor Cyan
Write-Host "  v3_mix_edla_gl 是主要 POS 設備" -ForegroundColor White
Write-Host "  原 POS 設備將被標記為「即將汰換」狀態" -ForegroundColor White
Write-Host ""

$confirm = Read-Host "確認要標記原 POS 設備為即將汰換？(Y/N)"
if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "已取消" -ForegroundColor Yellow
    exit 0
}

Write-Host "`n正在更新設備狀態..." -ForegroundColor Yellow

# 這裡需要透過 Odoo API 或直接操作資料庫來更新設備狀態
# 由於需要登入 Odoo，建議使用 Odoo UI 手動操作

Write-Host "`n建議操作方式：" -ForegroundColor Yellow
Write-Host "  1. 訪問 Odoo: http://$VMIP:8069/web/login" -ForegroundColor White
Write-Host "  2. 進入「基礎設施」→「設備」" -ForegroundColor White
Write-Host "  3. 找到原 POS 設備" -ForegroundColor White
Write-Host "  4. 編輯設備，將狀態改為「即將汰換 (Deprecated)」" -ForegroundColor White
Write-Host "  5. 取消勾選「主要設備」" -ForegroundColor White
Write-Host "  6. 在備註中說明已被 v3_mix_edla_gl 取代" -ForegroundColor White
Write-Host ""

Write-Host "或者使用 SQL 直接更新：" -ForegroundColor Yellow
Write-Host "  在 Odoo 中執行 SQL：" -ForegroundColor White
if ($OldPOSIP) {
    Write-Host "  UPDATE wuchang_infrastructure_device" -ForegroundColor Gray
    Write-Host "  SET status = 'deprecated', is_primary = false," -ForegroundColor Gray
    Write-Host "      note = note || '，已被 v3_mix_edla_gl 取代，即將汰換'" -ForegroundColor Gray
    Write-Host "  WHERE ip_address = '$OldPOSIP' AND device_type = 'pos';" -ForegroundColor Gray
} else {
    Write-Host "  UPDATE wuchang_infrastructure_device" -ForegroundColor Gray
    Write-Host "  SET status = 'deprecated', is_primary = false," -ForegroundColor Gray
    Write-Host "      note = note || '，已被 v3_mix_edla_gl 取代，即將汰換'" -ForegroundColor Gray
    Write-Host "  WHERE name = '$OldPOSName' AND device_type = 'pos';" -ForegroundColor Gray
}
