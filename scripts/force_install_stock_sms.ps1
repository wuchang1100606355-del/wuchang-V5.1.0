# Force Install stock_sms Module
# 合規要求：Google 非營利組織合規

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  🔧 強制安裝 stock_sms 模組" -ForegroundColor Cyan
Write-Host "  ✅ 合規: Google 非營利組織合規" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

cd "C:\wuchang V5.1.0"

# 方法一：重置所有 to install 模組狀態，然後只安裝 stock_sms
Write-Host "📋 步驟 1: 重置模組狀態..." -ForegroundColor Yellow

$resetSql = @"
BEGIN;
-- 重置所有 wuchang 模組為 uninstalled
UPDATE ir_module_module 
SET state = 'uninstalled' 
WHERE name LIKE 'wuchang_%' AND state = 'to install';

-- 保持 stock_sms 為 to install
UPDATE ir_module_module 
SET state = 'to install' 
WHERE name = 'stock_sms';

COMMIT;
"@

docker-compose exec -T db psql -U odoo -d admin -c $resetSql

Write-Host "`n📋 步驟 2: 檢查當前狀態..." -ForegroundColor Yellow
docker-compose exec -T db psql -U odoo -d admin -c "SELECT name, state FROM ir_module_module WHERE name = 'stock_sms' OR name LIKE 'wuchang_%' ORDER BY state, name;"

Write-Host "`n🔄 步驟 3: 重啟 Odoo 以安裝 stock_sms..." -ForegroundColor Yellow
docker-compose restart wuchang-web

Write-Host "`n⏳ 等待 Odoo 啟動 (20秒)..." -ForegroundColor Cyan
Start-Sleep -Seconds 20

Write-Host "`n✅ 步驟 4: 驗證 stock_sms 安裝狀態..." -ForegroundColor Green
docker-compose exec -T db psql -U odoo -d admin -c "SELECT name, state FROM ir_module_module WHERE name = 'stock_sms';"

Write-Host "`n🔍 步驟 5: 檢查字段是否可用..." -ForegroundColor Green
docker-compose exec -T db psql -U odoo -d admin -c "SELECT column_name FROM information_schema.columns WHERE table_name = 'res_config_settings' AND column_name = 'stock_move_sms_validation';"

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  ✅ 修復完成" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "💡 下一步操作:" -ForegroundColor Yellow
Write-Host "  1. 刷新瀏覽器頁面 (Ctrl+F5)" -ForegroundColor White
Write-Host "  2. 如果錯誤仍存在，請通過 Odoo UI 手動安裝:" -ForegroundColor White
Write-Host "     - 進入 設定 > 應用程式" -ForegroundColor White
Write-Host "     - 移除 '已安裝' 過濾器" -ForegroundColor White
Write-Host "     - 搜索 'SMS'" -ForegroundColor White
Write-Host "     - 找到 'SMS in Stock' 並點擊安裝" -ForegroundColor White
Write-Host ""
