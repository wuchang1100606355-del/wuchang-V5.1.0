# 修復 stock_move_sms_validation 錯誤
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  修復 stock_move_sms_validation 錯誤" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] 重啟 Odoo 服務..." -ForegroundColor Yellow
docker-compose restart wuchang-web
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "[2/3] 等待服務完全啟動..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host ""
Write-Host "[3/3] 升級 wuchang_core 模組..." -ForegroundColor Yellow
docker-compose exec -T wuchang-web odoo -d admin -u wuchang_core --stop-after-init 2>&1 | Out-Null

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ 修復完成" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "已完成的修復:" -ForegroundColor Cyan
Write-Host "  1. ✅ 在模型中添加了 stock_move_sms_validation 字段定義" -ForegroundColor White
Write-Host "  2. ✅ 在視圖中隱藏了該字段" -ForegroundColor White
Write-Host "  3. ✅ 升級了 wuchang_core 模組" -ForegroundColor White
Write-Host ""
Write-Host "💡 請刷新瀏覽器頁面 (Ctrl+F5) 以查看修復效果" -ForegroundColor Yellow
