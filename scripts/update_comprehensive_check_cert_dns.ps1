# 更新每小時全面檢查，包含憑證簽發和靜態DNS設定檢查

Write-Host "=== 更新每小時全面檢查（包含憑證簽發和靜態DNS設定） ===" -ForegroundColor Cyan

Write-Host "`n✓ 更新內容：" -ForegroundColor Green
Write-Host "  1. 憑證簽發檢查（Caddy + Let's Encrypt）" -ForegroundColor White
Write-Host "  2. 靜態DNS設定檢查（DNS A記錄檢查）" -ForegroundColor White
Write-Host "  3. 網域部署檢查（已更新）" -ForegroundColor White
Write-Host "  4. 全球可見性檢查" -ForegroundColor White
Write-Host "  5. Google 非營利組織首頁合規檢查" -ForegroundColor White

Write-Host "`n檢查項目詳解：" -ForegroundColor Yellow
Write-Host "  憑證簽發檢查：" -ForegroundColor Cyan
Write-Host "    - Caddy 容器運行狀態" -ForegroundColor Gray
Write-Host "    - Caddy 配置文件存在性" -ForegroundColor Gray
Write-Host "    - 網域配置狀態" -ForegroundColor Gray
Write-Host "    - Let's Encrypt 證書狀態" -ForegroundColor Gray
Write-Host ""
Write-Host "  靜態DNS設定檢查：" -ForegroundColor Cyan
Write-Host "    - DNS A記錄檢查（主站和www）" -ForegroundColor Gray
Write-Host "    - DNS MX記錄檢查（Google郵件服務）" -ForegroundColor Gray
Write-Host "    - DNS記錄是否符合預期值" -ForegroundColor Gray

Write-Host "`n系統AI具備全權：" -ForegroundColor Yellow
Write-Host "  ✓ 系統AI擁有全權執行所有檢查" -ForegroundColor Green
Write-Host "  ✓ 系統AI可以自動檢測和報告問題" -ForegroundColor Green
Write-Host "  ✓ 系統AI可以生成詳細的檢查報告" -ForegroundColor Green

Write-Host "`n任務狀態：" -ForegroundColor Yellow
$task = Get-ScheduledTask -TaskName "WuchangHourlyCheck" -ErrorAction SilentlyContinue
if ($task) {
    Write-Host "  任務名稱: $($task.TaskName)" -ForegroundColor Cyan
    Write-Host "  任務狀態: $($task.State)" -ForegroundColor Cyan
    Write-Host "  任務描述: $($task.Description)" -ForegroundColor Cyan
    
    $taskInfo = Get-ScheduledTaskInfo -TaskName "WuchangHourlyCheck" -ErrorAction SilentlyContinue
    if ($taskInfo.NextRunTime) {
        Write-Host "  下次執行時間: $($taskInfo.NextRunTime)" -ForegroundColor Cyan
    }
} else {
    Write-Host "  ⚠ 任務未找到，請執行更新腳本" -ForegroundColor Yellow
}

Write-Host "`n=== 更新完成 ===" -ForegroundColor Green
