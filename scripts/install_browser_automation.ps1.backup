# 安裝瀏覽器自動化環境
# 用途：安裝 Playwright 和瀏覽器驅動

Write-Host "`n=== 安裝瀏覽器自動化環境 ===" -ForegroundColor Cyan

# 檢查 Python
Write-Host "`n[1] 檢查 Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Python 未安裝" -ForegroundColor Red
    exit 1
}

# 安裝 Playwright
Write-Host "`n[2] 安裝 Playwright..." -ForegroundColor Yellow
try {
    pip install playwright>=1.40.0
    Write-Host "  ✅ Playwright 已安裝" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Playwright 安裝失敗: $_" -ForegroundColor Red
    exit 1
}

# 安裝瀏覽器驅動
Write-Host "`n[3] 安裝瀏覽器驅動..." -ForegroundColor Yellow
try {
    python -m playwright install chromium
    Write-Host "  ✅ Chromium 驅動已安裝" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ 瀏覽器驅動安裝失敗: $_" -ForegroundColor Yellow
    Write-Host "  可以稍後手動執行: python -m playwright install" -ForegroundColor Yellow
}

Write-Host "`n=== 安裝完成 ===" -ForegroundColor Green
Write-Host "`n使用方式：" -ForegroundColor Cyan
Write-Host "  1. 自動化納管設備:" -ForegroundColor White
Write-Host "     python scripts\auto_enroll_device_browser.py" -ForegroundColor Gray
Write-Host "`n  2. 自動化 Google Tasks:" -ForegroundColor White
Write-Host "     python scripts\auto_google_tasks.py" -ForegroundColor Gray
Write-Host "`n  3. 使用瀏覽器自動化類別:" -ForegroundColor White
Write-Host "     from browser_automation import BrowserAutomation" -ForegroundColor Gray
