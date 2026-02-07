# 列出所有回滾點
# 合規: 符合 Google 非營利組織合規要求

$rollbackIndexFile = "backups/rollback_points/rollback_index.json"

if (-not (Test-Path $rollbackIndexFile)) {
    Write-Host "未找到回滾點索引文件。" -ForegroundColor Yellow
    Write-Host "請先創建備份: .\scripts\create_backup_rollback.ps1" -ForegroundColor Cyan
    exit 0
}

$rollbackPoints = Get-Content $rollbackIndexFile | ConvertFrom-Json

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  系統回滾點列表" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "回滾點數量: $($rollbackPoints.Count)" -ForegroundColor Yellow
Write-Host ""

$index = 1
foreach ($point in $rollbackPoints) {
    Write-Host "[$index] $($point.name)" -ForegroundColor Green
    Write-Host "    時間: $($point.date)" -ForegroundColor White
    Write-Host "    類型: $($point.type)" -ForegroundColor White
    Write-Host "    路徑: $($point.path)" -ForegroundColor Gray
    Write-Host ""
    $index++
}

Write-Host "使用回滾點:" -ForegroundColor Yellow
Write-Host "  .\scripts\restore_from_rollback.ps1 <rollback_name>" -ForegroundColor Gray
Write-Host ""
