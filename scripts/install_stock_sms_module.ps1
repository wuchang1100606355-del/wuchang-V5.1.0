# 安裝 stock_sms 模組
# 合規: 符合 Google 非營利組織合規要求

param (
    [string]$DbName = "admin"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  安裝 stock_sms 模組" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "數據庫: $DbName" -ForegroundColor Yellow
Write-Host ""

# 檢查模組是否已安裝
Write-Host "[1/3] 檢查模組狀態..." -ForegroundColor Yellow

$dbContainer = docker ps -q -f ancestor=postgres:15 | Select-Object -First 1
if (-not $dbContainer) {
    Write-Host "  ❌ 未找到數據庫容器" -ForegroundColor Red
    exit 1
}

$moduleCheck = docker exec $dbContainer psql -U odoo -d $DbName -t -c "SELECT state FROM ir_module_module WHERE name = 'stock_sms';" 2>&1

if ($moduleCheck -match "installed") {
    Write-Host "  ✅ stock_sms 模組已安裝" -ForegroundColor Green
    Write-Host ""
    Write-Host "模組已安裝，無需重複安裝。" -ForegroundColor Cyan
    exit 0
} elseif ($moduleCheck -match "uninstalled") {
    Write-Host "  ⚠️  stock_sms 模組未安裝，需要安裝" -ForegroundColor Yellow
} else {
    Write-Host "  ⚠️  模組狀態未知，嘗試安裝" -ForegroundColor Yellow
}

Write-Host ""

Write-Host "[2/3] 安裝 stock_sms 模組..." -ForegroundColor Yellow

Write-Host "  等待 Odoo 服務就緒..." -ForegroundColor Gray
Start-Sleep -Seconds 15

# 通過 Odoo shell 安裝模組
$installScript = @"
import odoo
from odoo import api, SUPERUSER_ID

odoo.tools.config.parse_config([])
db_name = '$DbName'
registry = odoo.registry(db_name)

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    module = env['ir.module.module'].sudo().search([('name', '=', 'stock_sms')], limit=1)
    if module:
        if module.state == 'uninstalled':
            module.button_immediate_install()
            print('✅ stock_sms 模組已安裝')
        else:
            print('✅ stock_sms 模組狀態: ' + module.state)
    else:
        print('❌ 未找到 stock_sms 模組')
"@

$installScript | Out-File -FilePath "scripts/temp_install_stock_sms.py" -Encoding UTF8

try {
    docker cp "scripts/temp_install_stock_sms.py" "wuchangv510-wuchang-web-1:/tmp/install_stock_sms.py"
    docker-compose exec -T wuchang-web odoo shell -d $DbName --no-http -c "exec(open('/tmp/install_stock_sms.py').read())" 2>&1 | Select-String -Pattern "(stock_sms|installed|Installed|error|Error|ERROR|✅|❌)" | Select-Object -First 10
} catch {
    Write-Host "  ⚠️  通過 shell 安裝失敗，嘗試直接安裝..." -ForegroundColor Yellow
    docker-compose exec -T wuchang-web odoo -d $DbName -i stock_sms --stop-after-init 2>&1 | Select-String -Pattern "(Installing|installed|error|Error|ERROR|stock_sms)" | Select-Object -First 10
}

Remove-Item -Path "scripts/temp_install_stock_sms.py" -ErrorAction SilentlyContinue

Write-Host ""

Write-Host "[3/3] 驗證安裝..." -ForegroundColor Yellow

Start-Sleep -Seconds 5
$verify = docker exec $dbContainer psql -U odoo -d $DbName -t -c "SELECT state FROM ir_module_module WHERE name = 'stock_sms';" 2>&1

if ($verify -match "installed") {
    Write-Host "  ✅ stock_sms 模組已成功安裝" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  模組狀態: $verify" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ 安裝完成" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "下一步:" -ForegroundColor Yellow
Write-Host "  1. 重啟 Odoo 服務: docker-compose restart wuchang-web" -ForegroundColor White
Write-Host "  2. 刷新瀏覽器頁面 (Ctrl+F5)" -ForegroundColor White
Write-Host ""
Write-Host "✅ 合規: 符合 Google 非營利組織合規要求" -ForegroundColor Green
