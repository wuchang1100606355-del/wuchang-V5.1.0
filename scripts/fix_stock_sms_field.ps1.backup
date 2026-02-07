# 修復 stock_move_sms_validation 字段
# 合規: 符合 Google 非營利組織合規要求

param (
    [string]$DbName = "admin"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  修復 stock_move_sms_validation 字段" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$dbContainer = docker ps -q -f ancestor=postgres:15 | Select-Object -First 1

if (-not $dbContainer) {
    Write-Host "❌ 未找到數據庫容器" -ForegroundColor Red
    exit 1
}

Write-Host "數據庫容器: $dbContainer" -ForegroundColor Cyan
Write-Host "數據庫名稱: $DbName" -ForegroundColor Cyan
Write-Host ""

# 檢查字段是否存在
Write-Host "[1/3] 檢查字段狀態..." -ForegroundColor Yellow

$checkField = docker exec $dbContainer psql -U odoo -d $DbName -t -c "SELECT COUNT(*) FROM information_schema.columns WHERE table_name='res_config_settings' AND column_name='stock_move_sms_validation';" 2>&1

if ($checkField -match "1") {
    Write-Host "  ✅ 字段已存在" -ForegroundColor Green
    Write-Host ""
    Write-Host "字段已存在，無需修復。" -ForegroundColor Cyan
    exit 0
} else {
    Write-Host "  ❌ 字段不存在，需要添加" -ForegroundColor Red
}

Write-Host ""

# 添加字段
Write-Host "[2/3] 添加字段..." -ForegroundColor Yellow

$sql = @"
-- 添加 stock_move_sms_validation 字段
ALTER TABLE res_config_settings 
ADD COLUMN IF NOT EXISTS stock_move_sms_validation boolean DEFAULT false;

-- 添加註釋
COMMENT ON COLUMN res_config_settings.stock_move_sms_validation IS '庫存移動 SMS 驗證 (兼容字段)';
"@

$result = docker exec $dbContainer psql -U odoo -d $DbName -c "$sql" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ 字段添加成功" -ForegroundColor Green
} else {
    Write-Host "  ❌ 字段添加失敗" -ForegroundColor Red
    Write-Host "  錯誤: $result" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 驗證字段
Write-Host "[3/3] 驗證字段..." -ForegroundColor Yellow

$verify = docker exec $dbContainer psql -U odoo -d $DbName -t -c "SELECT COUNT(*) FROM information_schema.columns WHERE table_name='res_config_settings' AND column_name='stock_move_sms_validation';" 2>&1

if ($verify -match "1") {
    Write-Host "  ✅ 字段驗證成功" -ForegroundColor Green
} else {
    Write-Host "  ❌ 字段驗證失敗" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ 字段修復完成" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "下一步:" -ForegroundColor Yellow
Write-Host "  1. 重啟 Odoo 服務: docker-compose restart wuchang-web" -ForegroundColor White
Write-Host "  2. 刷新瀏覽器頁面 (Ctrl+F5)" -ForegroundColor White
Write-Host ""
Write-Host "✅ 合規: 符合 Google 非營利組織合規要求" -ForegroundColor Green
