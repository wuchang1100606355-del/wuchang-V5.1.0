# 快速設定環境變數（連接真實根伺服器）
# 使用方式：修改下方變數值後執行此腳本

Write-Host "========================================"
Write-Host "五常系統 - 快速環境變數設定"
Write-Host "========================================"
Write-Host ""

# ========================================
# 請修改以下變數為您的實際值
# ========================================

# 伺服器健康檢查 URL（例如：https://wuchang.life/health）
$HealthUrl = "https://wuchang.life/health"

# 伺服器接收資料夾路徑（SMB/掛載磁碟，例如：\\SERVER\share\wuchang）
$CopyTo = "\\SERVER\share\wuchang"

# Hub URL（選填）
$HubUrl = ""

# Hub Token（選填）
$HubToken = ""

# ========================================
# 以下為自動設定部分，無需修改
# ========================================

Write-Host "設定環境變數..."
Write-Host ""

# 設定當前會話環境變數
$env:WUCHANG_HEALTH_URL = $HealthUrl
$env:WUCHANG_COPY_TO = $CopyTo

if ($HubUrl) {
    $env:WUCHANG_HUB_URL = $HubUrl
}
if ($HubToken) {
    $env:WUCHANG_HUB_TOKEN = $HubToken
}

Write-Host "[OK] WUCHANG_HEALTH_URL = $HealthUrl"
Write-Host "[OK] WUCHANG_COPY_TO = $CopyTo"
if ($HubUrl) {
    Write-Host "[OK] WUCHANG_HUB_URL = $HubUrl"
}
if ($HubToken) {
    Write-Host "[OK] WUCHANG_HUB_TOKEN = *** (已隱藏)"
}

Write-Host ""
Write-Host "========================================"
Write-Host "環境變數設定完成（當前會話）"
Write-Host "========================================"
Write-Host ""
Write-Host "驗證設定："
Write-Host "  python setup_env_vars.py status"
Write-Host ""
Write-Host "檢查伺服器連接："
Write-Host "  python check_server_connection.py"
Write-Host ""
Write-Host "檢查版本差距："
Write-Host "  python check_version_diff.py --profile kb"
Write-Host "  python check_version_diff.py --profile rules"
Write-Host ""
