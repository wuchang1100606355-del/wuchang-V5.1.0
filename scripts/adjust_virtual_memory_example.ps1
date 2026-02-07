# 調整虛擬記憶體（需要管理員權限）
# 注意：此操作需要重新啟動電腦

$computerSystem = Get-CimInstance -ClassName Win32_ComputerSystem
$pageFile = Get-CimInstance -ClassName Win32_PageFileSetting -Filter "Name='C:\\\\pagefile.sys'"

if (-not $pageFile) {
    Write-Host "未找到分頁檔案，需要手動建立" -ForegroundColor Yellow
    exit
}

# 設定建議大小（GB）
$initialSize = 12 * 1024  # 轉換為 MB
$maximumSize = 16 * 1024  # 轉換為 MB

Write-Host "設定虛擬記憶體大小：" -ForegroundColor Cyan
Write-Host "  初始大小: $initialSize MB (~12 GB)" -ForegroundColor White
Write-Host "  最大大小: $maximumSize MB (~16 GB)" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  此操作需要重新啟動電腦才能生效" -ForegroundColor Yellow
