# 驗證環境變數設定
# 使用方式：在設定環境變數後，在同一個 PowerShell 會話中執行此腳本

Write-Host "========================================"
Write-Host "環境變數驗證"
Write-Host "========================================"
Write-Host ""

$healthUrl = $env:WUCHANG_HEALTH_URL
$copyTo = $env:WUCHANG_COPY_TO
$hubUrl = $env:WUCHANG_HUB_URL
$hubToken = $env:WUCHANG_HUB_TOKEN

$allSet = $true

if ($healthUrl) {
    Write-Host "[OK] WUCHANG_HEALTH_URL = $healthUrl" -ForegroundColor Green
} else {
    Write-Host "[X] WUCHANG_HEALTH_URL 未設定" -ForegroundColor Red
    $allSet = $false
}

if ($copyTo) {
    Write-Host "[OK] WUCHANG_COPY_TO = $copyTo" -ForegroundColor Green
} else {
    Write-Host "[X] WUCHANG_COPY_TO 未設定" -ForegroundColor Red
    $allSet = $false
}

if ($hubUrl) {
    Write-Host "[OK] WUCHANG_HUB_URL = $hubUrl" -ForegroundColor Green
} else {
    Write-Host "[提示] WUCHANG_HUB_URL 未設定（選填）" -ForegroundColor Yellow
}

if ($hubToken) {
    Write-Host "[OK] WUCHANG_HUB_TOKEN = *** (已設定)" -ForegroundColor Green
} else {
    Write-Host "[提示] WUCHANG_HUB_TOKEN 未設定（選填）" -ForegroundColor Yellow
}

Write-Host ""

if ($allSet) {
    Write-Host "========================================"
    Write-Host "環境變數設定完成！" -ForegroundColor Green
    Write-Host "========================================"
    Write-Host ""
    Write-Host "下一步："
    Write-Host "  1. 檢查伺服器連接："
    Write-Host "     python check_server_connection.py"
    Write-Host ""
    Write-Host "  2. 檢查版本差距："
    Write-Host "     python check_version_diff.py --profile kb"
    Write-Host "     python check_version_diff.py --profile rules"
    Write-Host ""
    Write-Host "  3. 執行擇優同步："
    Write-Host "     python smart_sync.py --profile kb"
    Write-Host ""
} else {
    Write-Host "========================================"
    Write-Host "環境變數未完全設定" -ForegroundColor Red
    Write-Host "========================================"
    Write-Host ""
    Write-Host "請執行設定腳本："
    Write-Host "  .\setup_file_sync_env.ps1"
    Write-Host ""
    Write-Host "或手動設定："
    Write-Host '  $env:WUCHANG_HEALTH_URL = "https://wuchang.life/health"'
    Write-Host '  $env:WUCHANG_COPY_TO = "\\SERVER\share\wuchang"'
    Write-Host ""
}
