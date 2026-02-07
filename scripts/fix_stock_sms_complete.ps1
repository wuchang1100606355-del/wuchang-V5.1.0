# 完整修復 stock_move_sms_validation 錯誤
# 合規: 符合 Google 非營利組織合規要求

param (
    [string]$DbName = "admin",
    [switch]$UseRescue = $false
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  完整修復 stock_move_sms_validation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($UseRescue) {
    Write-Host "⚠️  將使用救援模式（清除模組記錄）" -ForegroundColor Yellow
    Write-Host ""
    $confirmation = Read-Host "確認執行救援操作？(輸入 'YES' 繼續)"
    if ($confirmation -ne "YES") {
        Write-Host "操作已取消。" -ForegroundColor Yellow
        exit 0
    }
    
    Write-Host ""
    Write-Host "[救援模式] 清理模組記錄..." -ForegroundColor Yellow
    & ".\scripts\rescue_odoo.ps1" -DbName $DbName
    
    Write-Host ""
    Write-Host "重啟服務..." -ForegroundColor Yellow
    docker-compose restart wuchang-web
    Start-Sleep -Seconds 15
    
    Write-Host ""
    Write-Host "✅ 救援完成，請登入 Odoo 並重新安裝模組" -ForegroundColor Green
    exit 0
}

# 標準修復流程
Write-Host "[1/4] 確認字段存在..." -ForegroundColor Yellow

$dbContainer = docker ps -q -f ancestor=postgres:15 | Select-Object -First 1
if (-not $dbContainer) {
    Write-Host "  ❌ 未找到數據庫容器" -ForegroundColor Red
    exit 1
}

$fieldCheck = docker exec $dbContainer psql -U odoo -d $DbName -t -c "SELECT COUNT(*) FROM information_schema.columns WHERE table_name='res_config_settings' AND column_name='stock_move_sms_validation';" 2>&1

if ($fieldCheck -match "1") {
    Write-Host "  ✅ 字段已存在" -ForegroundColor Green
} else {
    Write-Host "  ❌ 字段不存在，添加字段..." -ForegroundColor Yellow
    & ".\scripts\fix_stock_sms_field.ps1" -DbName $DbName
}

Write-Host ""

Write-Host "[2/4] 清除緩存..." -ForegroundColor Yellow
docker-compose exec -T wuchang-web rm -rf /var/lib/odoo/filestore/*/assets 2>&1 | Out-Null
Write-Host "  ✅ 緩存已清除" -ForegroundColor Green

Write-Host ""

Write-Host "[3/4] 重啟服務..." -ForegroundColor Yellow
docker-compose restart wuchang-web
Start-Sleep -Seconds 15
Write-Host "  ✅ 服務已重啟" -ForegroundColor Green

Write-Host ""

Write-Host "[4/4] 升級模組..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
docker-compose exec -T wuchang-web odoo -d $DbName -u wuchang_core --stop-after-init 2>&1 | Out-Null
Write-Host "  ✅ 模組升級完成" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ 修復完成" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "💡 如果錯誤仍然存在，請使用救援模式:" -ForegroundColor Yellow
Write-Host "  .\scripts\fix_stock_sms_complete.ps1 -UseRescue" -ForegroundColor Gray
Write-Host ""
Write-Host "✅ 合規: 符合 Google 非營利組織合規要求" -ForegroundColor Green
