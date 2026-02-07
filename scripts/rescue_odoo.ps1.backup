# Odoo 救援腳本
# 用途: 從數據庫中移除所有 Wuchang 模組記錄以修復啟動錯誤
# 警告: 這是破壞性操作，會清除模組註冊信息
# 合規: 符合 Google 非營利組織合規要求

# Usage: .\scripts\rescue_odoo.ps1 <db_name>
param (
    [string]$DbName = "admin"
)

Write-Host "========================================" -ForegroundColor Red
Write-Host "  Odoo 救援操作 (RESCUE Operation)" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Red
Write-Host ""
Write-Host "⚠️  警告: 這是破壞性操作！" -ForegroundColor Red
Write-Host "此腳本將從數據庫中移除所有 Wuchang 模組的註冊記錄。" -ForegroundColor Yellow
Write-Host "這將修復啟動錯誤，但模組需要重新安裝。" -ForegroundColor Cyan
Write-Host ""

# 確認操作
$confirmation = Read-Host "確認執行救援操作？(輸入 'YES' 繼續，其他任何輸入將取消)"
if ($confirmation -ne "YES") {
    Write-Host "操作已取消。" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "開始執行救援操作..." -ForegroundColor Yellow
Write-Host "數據庫: $DbName" -ForegroundColor Cyan
Write-Host ""

# SQL to remove all wuchang modules from DB registry
$sql = @"
BEGIN;
DELETE FROM ir_model_data WHERE module LIKE 'wuchang_%';
DELETE FROM ir_module_module_dependency WHERE name LIKE 'wuchang_%';
DELETE FROM ir_module_module_dependency WHERE module_id IN (SELECT id FROM ir_module_module WHERE name LIKE 'wuchang_%');
DELETE FROM ir_module_module WHERE name LIKE 'wuchang_%';
COMMIT;
"@

try {
    # Try to find the DB container
    $containerName = docker ps -q -f ancestor=postgres:15 | Select-Object -First 1

    if (-not $containerName) {
        Write-Host "❌ 錯誤: 未找到數據庫容器！Docker 是否正在運行？" -ForegroundColor Red
        exit 1
    }

    Write-Host "找到數據庫容器: $containerName" -ForegroundColor Cyan
    Write-Host ""

    # Execute SQL
    Write-Host "執行 SQL 清理操作..." -ForegroundColor Yellow
    docker exec -i $containerName psql -U odoo -d "$DbName" -c "$sql"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  ✅ 救援操作成功完成" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "所有 Wuchang 模組記錄已從數據庫中移除。" -ForegroundColor Cyan
        Write-Host "現在可以登入到乾淨的 Odoo 系統。" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "下一步操作:" -ForegroundColor Yellow
        Write-Host "  1. 重啟 Odoo: docker-compose restart wuchang-web" -ForegroundColor White
        Write-Host "  2. 登入 Odoo 後台" -ForegroundColor White
        Write-Host "  3. 重新安裝 Wuchang 模組" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "❌ 錯誤: SQL 執行失敗。" -ForegroundColor Red
        Write-Host "請檢查數據庫名稱 (默認: admin)" -ForegroundColor Yellow
        Write-Host "使用方式: .\scripts\rescue_odoo.ps1 <db_name>" -ForegroundColor Gray
        exit 1
    }

} catch {
    Write-Host ""
    Write-Host "❌ 錯誤: 腳本執行失敗" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
