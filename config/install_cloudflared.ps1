# 安裝 cloudflared 腳本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "安裝 cloudflared" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$downloadUrl = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
$installPath = "$env:ProgramFiles\Cloudflared\cloudflared.exe"
$installDir = "$env:ProgramFiles\Cloudflared"

# 檢查是否已安裝
if (Test-Path $installPath) {
    Write-Host "[✓] cloudflared 已安裝: $installPath" -ForegroundColor Green
    & $installPath --version
    exit 0
}

Write-Host "[!] cloudflared 未安裝，開始下載..." -ForegroundColor Yellow
Write-Host ""

# 建立安裝目錄
if (-not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
}

# 下載檔案
$tempFile = "$env:TEMP\cloudflared-windows-amd64.exe"
Write-Host "[...] 下載 cloudflared..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri $downloadUrl -OutFile $tempFile -UseBasicParsing
    Write-Host "[✓] 下載完成" -ForegroundColor Green
} catch {
    Write-Host "[✗] 下載失敗: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "請手動下載:" -ForegroundColor Yellow
    Write-Host "  https://github.com/cloudflare/cloudflared/releases/latest" -ForegroundColor Cyan
    exit 1
}

# 複製到安裝目錄
Copy-Item $tempFile $installPath -Force
Remove-Item $tempFile -Force

# 加入 PATH（僅本次會話）
$env:Path += ";$installDir"

# 驗證安裝
Write-Host ""
Write-Host "[✓] 安裝完成: $installPath" -ForegroundColor Green
& $installPath --version

Write-Host ""
Write-Host "注意：需要重新開啟 PowerShell 或新增到系統 PATH" -ForegroundColor Yellow
Write-Host "或使用完整路徑執行: $installPath" -ForegroundColor Yellow
