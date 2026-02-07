# ==============================================================================
# Wuchang OS v5.0.0 - Rapid Deployment Protocol (Twin-Turbo) - PowerShell Edition
# ==============================================================================

Write-Host ">>> [1/3] 啟動五常熱部署協議 (Initiating Hot-Deploy)..." -ForegroundColor Cyan

# 定義要更新的模組列表
$MODULES = "wuchang_core,wuchang_business,wuchang_web_portal"

Write-Host ">>> [2/3] 正在更新資料庫結構 (Database Schema Update)..." -ForegroundColor Cyan
Write-Host "    Target Modules: $MODULES" -ForegroundColor Gray

# 使用 docker-compose run 開一個新容器來執行升級
docker-compose run --rm wuchang-web odoo -u $MODULES --stop-after-init --db_host=db --db_user=odoo --db_password=odoo

if ($LASTEXITCODE -eq 0) {
    Write-Host ">>> [3/3] 資料庫更新成功！正在重啟 Web 節點..." -ForegroundColor Green
    docker-compose restart wuchang-web
    Write-Host ">>> 部署完成 (Deployment Complete)！" -ForegroundColor Green
    Write-Host "    請訪問: http://localhost:8069" -ForegroundColor Yellow
} else {
    Write-Host "!!! [ERROR] 資料庫更新失敗，請檢查日誌。" -ForegroundColor Red
    exit 1
}
